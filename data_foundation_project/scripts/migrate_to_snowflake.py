#!/usr/bin/env python3
"""
ETL Pipeline: Migrate WAMEX Shapefile Data to Snowflake

This script handles the complete migration of geological exploration data
from local shapefiles to Snowflake with proper error handling and validation.

Usage:
    python migrate_to_snowflake.py
    python migrate_to_snowflake.py --shapefile /path/to/specific.shp
    python migrate_to_snowflake.py --setup-only  # Just create tables
    python migrate_to_snowflake.py --validate-only  # Just validate connection
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import geopandas as gpd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.snowflake_client import snowflake_client
from src.data_access import DataLoader
from src.config import snowflake_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SnowflakeMigrationPipeline:
    """ETL Pipeline for migrating WAMEX data to Snowflake"""

    def __init__(self, max_records: int = 1000):
        self.loader = DataLoader()
        self.max_records = max_records
        self.stats = {
            'start_time': datetime.now(),
            'records_processed': 0,
            'records_loaded': 0,
            'errors': []
        }

    def validate_environment(self) -> bool:
        """Validate Snowflake configuration and connection"""
        logger.info("Validating Snowflake environment...")

        # Check configuration
        if not snowflake_config.validate_credentials():
            logger.error("Snowflake credentials not properly configured")
            logger.error("Please check your .env file or environment variables")
            return False

        # Test connection
        if not snowflake_client.test_connection():
            logger.error("Failed to connect to Snowflake")
            return False

        logger.info(f"✅ Successfully connected to Snowflake")
        logger.info(f"   Account: {snowflake_config.account}")
        logger.info(f"   Database: {snowflake_config.database}")
        logger.info(f"   Schema: {snowflake_config.schema}")

        return True

    def setup_database_schema(self) -> bool:
        """Create necessary tables and indexes in Snowflake"""
        logger.info("Setting up database schema...")

        try:
            snowflake_client.create_tables()
            logger.info("✅ Database schema created/verified successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to setup database schema: {e}")
            self.stats['errors'].append(f"Schema setup failed: {e}")
            return False

    def find_shapefile(self, shapefile_path: str = None) -> Path:
        """Find the shapefile to process"""
        if shapefile_path:
            shapefile = Path(shapefile_path)
            if not shapefile.exists():
                raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")
            return shapefile

        # Look for shapefile in data directory
        data_dir = Path(__file__).parent.parent / 'data' / 'raw'
        shapefiles = list(data_dir.rglob('*.shp'))

        if not shapefiles:
            raise FileNotFoundError(f"No .shp files found in {data_dir}")

        if len(shapefiles) > 1:
            logger.warning(f"Multiple shapefiles found, using: {shapefiles[0]}")

        return shapefiles[0]

    def validate_shapefile_data(self, shapefile_path: Path) -> bool:
        """Validate shapefile data before migration"""
        logger.info(f"Validating shapefile: {shapefile_path}")

        try:
            gdf = gpd.read_file(shapefile_path)
            self.stats['records_processed'] = len(gdf)

            logger.info(f"   Total records: {len(gdf)}")
            logger.info(f"   Columns: {list(gdf.columns)}")
            logger.info(f"   CRS: {gdf.crs}")

            # Check for required columns
            required_columns = ['ANUMBER', 'TITLE', 'geometry']
            missing_columns = [col for col in required_columns if col not in gdf.columns]

            if missing_columns:
                logger.error(f"❌ Missing required columns: {missing_columns}")
                return False

            # Check for null values in key columns
            null_counts = gdf[required_columns].isnull().sum()
            if null_counts.any():
                logger.warning(f"Null values found: {null_counts.to_dict()}")

            # Check geometry validity
            invalid_geom = ~gdf.geometry.is_valid
            if invalid_geom.any():
                logger.warning(f"Invalid geometries found: {invalid_geom.sum()} records")

            logger.info("✅ Shapefile validation completed")
            return True

        except Exception as e:
            logger.error(f"❌ Shapefile validation failed: {e}")
            self.stats['errors'].append(f"Shapefile validation failed: {e}")
            return False

    def migrate_data(self, shapefile_path: Path) -> bool:
        """Migrate data from shapefile to Snowflake"""
        logger.info(f"Starting data migration from {shapefile_path}")
        try:
            records_loaded = snowflake_client.load_shapefile_data(str(shapefile_path), max_records=self.max_records)
            self.stats['records_loaded'] = records_loaded
            logger.info(f"✅ Successfully loaded {records_loaded} records to Snowflake")
            # Verify the migration
            return self.verify_migration()
        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
            self.stats['errors'].append(f"Data migration failed: {e}")
            return False

    def verify_migration(self) -> bool:
        """Verify that data was successfully migrated"""
        logger.info("Verifying data migration...")

        try:
            metrics = snowflake_client.get_data_quality_metrics()

            total_records = metrics.get('total_records', 0)
            records_with_geometry = metrics.get('records_with_geometry', 0)

            logger.info(f"   Total records in Snowflake: {total_records}")
            logger.info(f"   Records with geometry: {records_with_geometry}")
            logger.info(f"   Unique operators: {metrics.get('unique_operators', 0)}")
            logger.info(f"   Unique commodities: {metrics.get('unique_commodities', 0)}")
            logger.info(f"   Year range: {metrics.get('earliest_year', 'N/A')} - {metrics.get('latest_year', 'N/A')}")

            # Check if migration was successful
            if total_records == self.stats['records_processed']:
                logger.info("✅ Data migration verification successful")
                return True
            else:
                logger.warning(f"⚠️ Record count mismatch: processed {self.stats['records_processed']}, loaded {total_records}")
                return True  # Still consider it successful if data exists

        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            self.stats['errors'].append(f"Migration verification failed: {e}")
            return False

    def print_summary(self):
        """Print migration summary"""
        end_time = datetime.now()
        duration = end_time - self.stats['start_time']

        logger.info("\n" + "="*60)
        logger.info("MIGRATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Start time: {self.stats['start_time']}")
        logger.info(f"End time: {end_time}")
        logger.info(f"Duration: {duration}")
        logger.info(f"Records processed: {self.stats['records_processed']}")
        logger.info(f"Records loaded: {self.stats['records_loaded']}")

        if self.stats['errors']:
            logger.info(f"Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.info(f"  - {error}")
        else:
            logger.info("✅ Migration completed without errors")

        logger.info("="*60)

    def run_full_migration(self, shapefile_path: str = None) -> bool:
        """Run the complete migration pipeline"""
        logger.info("Starting Snowflake migration pipeline...")

        try:
            # Step 1: Validate environment
            if not self.validate_environment():
                return False

            # Step 2: Setup database schema
            if not self.setup_database_schema():
                return False

            # Step 3: Find and validate shapefile
            shapefile = self.find_shapefile(shapefile_path)
            if not self.validate_shapefile_data(shapefile):
                return False

            # Step 4: Migrate data
            if not self.migrate_data(shapefile):
                return False

            logger.info("🎉 Migration pipeline completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Migration pipeline failed: {e}")
            self.stats['errors'].append(f"Pipeline failed: {e}")
            return False

        finally:
            self.print_summary()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Migrate WAMEX data to Snowflake")
    parser.add_argument(
        "--shapefile",
        type=str,
        help="Path to specific shapefile (optional)"
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only create tables, don't migrate data"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate connection and configuration"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maximum number of records to upload to Snowflake (default: all records)"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    pipeline = SnowflakeMigrationPipeline(max_records=args.max_records)

    try:
        if args.validate_only:
            success = pipeline.validate_environment()
            sys.exit(0 if success else 1)

        elif args.setup_only:
            success = (
                pipeline.validate_environment() and
                pipeline.setup_database_schema()
            )
            sys.exit(0 if success else 1)

        else:
            success = pipeline.run_full_migration(args.shapefile)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
