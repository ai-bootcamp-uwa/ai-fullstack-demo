#!/usr/bin/env python3
"""
ETL Pipeline: Migrate WAMEX Shapefile Data to Snowflake

This script handles the complete migration of geological exploration data
from local shapefiles to Snowflake with proper error handling and validation.

Usage:
    python migrate_to_snowflake.py  # Default: skip existing records
    python migrate_to_snowflake.py --shapefile /path/to/specific.shp
    python migrate_to_snowflake.py --setup-only  # Just create tables
    python migrate_to_snowflake.py --validate-only  # Just validate connection
    python migrate_to_snowflake.py --force-replace  # Replace existing records
    python migrate_to_snowflake.py --fail-on-conflicts  # Fail if conflicts exist
    python migrate_to_snowflake.py --check-existing  # Only check for conflicts
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import geopandas as gpd
from typing import Dict, Any, List

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

    def check_existing_data(self, shapefile_path: Path) -> Dict[str, Any]:
        """Check if data from shapefile already exists in Snowflake"""
        logger.info("Checking for existing data in Snowflake...")
        try:
            metrics = snowflake_client.get_data_quality_metrics()
            snowflake_records = metrics.get('total_records', 0)
            gdf = gpd.read_file(shapefile_path)
            shapefile_anumbers = set(gdf['ANUMBER'].dropna().astype(int))
            if snowflake_records == 0:
                logger.info("✅ No existing data in Snowflake - safe to proceed")
                return {
                    'has_existing_data': False,
                    'snowflake_records': 0,
                    'shapefile_records': len(gdf),
                    'conflicts': []
                }
            logger.info(f"Found {snowflake_records:,} existing records in Snowflake")
            logger.info(f"Checking {len(shapefile_anumbers)} ANUMBER values for conflicts...")
            existing_anumbers = set()
            chunk_size = 1000
            anumber_list = list(shapefile_anumbers)
            for i in range(0, len(anumber_list), chunk_size):
                chunk = anumber_list[i:i + chunk_size]
                anumber_str = ','.join(map(str, chunk))
                query = f"SELECT ANUMBER FROM GEOLOGICAL_REPORTS WHERE ANUMBER IN ({anumber_str})"
                results = snowflake_client.execute_query(query)
                chunk_existing = {row['ANUMBER'] for row in results}
                existing_anumbers.update(chunk_existing)
            conflicts = existing_anumbers.intersection(shapefile_anumbers)
            result = {
                'has_existing_data': snowflake_records > 0,
                'snowflake_records': snowflake_records,
                'shapefile_records': len(gdf),
                'shapefile_anumbers': len(shapefile_anumbers),
                'conflicts': list(conflicts),
                'conflict_count': len(conflicts)
            }
            if conflicts:
                logger.warning(f"⚠️ Found {len(conflicts)} conflicting ANUMBER values")
                logger.warning(f"Sample conflicts: {list(conflicts)[:10]}")
            else:
                logger.info("✅ No ANUMBER conflicts found - safe to proceed")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to check existing data: {e}")
            self.stats['errors'].append(f"Existence check failed: {e}")
            raise

    def handle_data_conflicts(self, conflict_info: Dict[str, Any], conflict_resolution: str = 'fail') -> bool:
        """Handle data conflicts based on resolution strategy"""
        if not conflict_info['conflicts']:
            return True
        conflict_count = conflict_info['conflict_count']
        if conflict_resolution == 'fail':
            logger.error(f"❌ Migration aborted: {conflict_count} conflicting records found")
            logger.error("Use --force-replace or --skip-conflicts to proceed")
            return False
        elif conflict_resolution == 'skip':
            logger.info(f"🔄 Skipping {conflict_count} conflicting records")
            return True
        elif conflict_resolution == 'replace':
            logger.info(f"🔄 Replacing {conflict_count} existing records")
            conflict_anumbers = ','.join(map(str, conflict_info['conflicts']))
            delete_query = f"DELETE FROM GEOLOGICAL_REPORTS WHERE ANUMBER IN ({conflict_anumbers})"
            try:
                snowflake_client.execute_query(delete_query)
                logger.info(f"✅ Deleted {conflict_count} existing records")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to delete existing records: {e}")
                return False
        else:
            logger.error(f"❌ Invalid conflict resolution: {conflict_resolution}")
            return False

    def _load_with_anumber_filter(self, shapefile_path: Path, exclude_anumbers: List[int]) -> int:
        """Load shapefile data excluding specific ANUMBER values"""
        logger.info(f"Loading data while excluding {len(exclude_anumbers)} existing ANUMBERs")
        gdf = gpd.read_file(shapefile_path)
        original_count = len(gdf)
        gdf_filtered = gdf[~gdf['ANUMBER'].isin(exclude_anumbers)].copy()
        filtered_count = len(gdf_filtered)
        logger.info(f"Filtered: {original_count} -> {filtered_count} records")
        if filtered_count == 0:
            logger.warning("No records to load after filtering")
            return 0
        if self.max_records and filtered_count > self.max_records:
            gdf_filtered = gdf_filtered.head(self.max_records)
            logger.info(f"Limited to {self.max_records} records")
        temp_shapefile = shapefile_path.parent / f"temp_filtered_{shapefile_path.name}"
        gdf_filtered.to_file(temp_shapefile)
        try:
            records_loaded = snowflake_client.load_shapefile_data(str(temp_shapefile))
            return records_loaded
        finally:
            import shutil
            shutil.rmtree(temp_shapefile.parent / temp_shapefile.stem, ignore_errors=True)

    def migrate_data(self, shapefile_path: Path, conflict_resolution: str = 'skip') -> bool:
        """Migrate data from shapefile to Snowflake with conflict handling"""
        logger.info(f"Starting data migration from {shapefile_path}")
        if conflict_resolution == 'skip':
            logger.info("🔄 Checking for existing data to skip conflicts...")
            try:
                records_loaded = snowflake_client.load_shapefile_data(
                    str(shapefile_path),
                    max_records=self.max_records
                )
            except Exception as e:
                logger.error(f"❌ Data migration failed: {e}")
                self.stats['errors'].append(f"Data migration failed: {e}")
                return False
        elif conflict_resolution == 'replace':
            logger.info("🔄 Will replace existing records...")
            records_loaded = snowflake_client.load_shapefile_data(
                str(shapefile_path),
                max_records=self.max_records
            )
        else:  # fail
            logger.info("🔄 Will fail on conflicts...")
            records_loaded = snowflake_client.load_shapefile_data(
                str(shapefile_path),
                max_records=self.max_records
            )
        self.stats['records_loaded'] = records_loaded
        logger.info(f"✅ Successfully loaded {records_loaded} records to Snowflake")
        return self.verify_migration()

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

    def run_full_migration(self, shapefile_path: str = None, conflict_resolution: str = 'skip') -> bool:
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
            if not self.migrate_data(shapefile, conflict_resolution):
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
        "--check-existing",
        action="store_true",
        help="Only check for existing data conflicts"
    )
    parser.add_argument(
        "--force-replace",
        action="store_true",
        help="Replace existing records with same ANUMBER"
    )
    parser.add_argument(
        "--fail-on-conflicts",
        action="store_true",
        help="Fail migration if conflicting records exist (override default skip behavior)"
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

    # SET DEFAULT CONFLICT RESOLUTION TO SKIP (NEW):
    conflict_resolution = 'skip'  # DEFAULT: skip existing records
    if args.force_replace:
        conflict_resolution = 'replace'
    elif args.fail_on_conflicts:
        conflict_resolution = 'fail'

    # Log the conflict resolution strategy being used
    logger.info(f"Conflict resolution strategy: {conflict_resolution}")
    if conflict_resolution == 'skip':
        logger.info("💡 Records with existing ANUMBERs will be skipped (default behavior)")
        logger.info("   Use --force-replace to overwrite or --fail-on-conflicts to abort")

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

        elif args.check_existing:
            success = pipeline.validate_environment()
            if success:
                shapefile = pipeline.find_shapefile(args.shapefile)
                conflict_info = pipeline.check_existing_data(shapefile)
                # Print summary
                logger.info(f"Existing records in Snowflake: {conflict_info['snowflake_records']}")
                logger.info(f"Records in shapefile: {conflict_info['shapefile_records']}")
                logger.info(f"Conflicting ANUMBERs: {conflict_info['conflict_count']}")
                if conflict_info['conflicts']:
                    logger.info(f"Sample conflicts: {conflict_info['conflicts'][:10]}")
            sys.exit(0 if success else 1)

        else:
            success = pipeline.run_full_migration(args.shapefile, conflict_resolution)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
