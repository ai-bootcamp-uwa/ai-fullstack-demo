import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class SnowflakeConfig(BaseModel):
    """Snowflake database configuration"""
    account: str = Field(default_factory=lambda: os.getenv("SNOWFLAKE_ACCOUNT", ""))
    user: str = Field(default_factory=lambda: os.getenv("SNOWFLAKE_USER", ""))
    password: str = Field(default_factory=lambda: os.getenv("SNOWFLAKE_PASSWORD", ""))
    warehouse: str = Field(default_factory=lambda: os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"))
    database: str = Field(default_factory=lambda: os.getenv("SNOWFLAKE_DATABASE", "WAMEX_EXPLORATION"))
    schema: str = Field(default_factory=lambda: os.getenv("SNOWFLAKE_SCHEMA", "GEOSPATIAL_DATA"))
    role: Optional[str] = Field(default_factory=lambda: os.getenv("SNOWFLAKE_ROLE", "DATA_ENGINEER"))
    authenticator: Optional[str] = Field(default_factory=lambda: os.getenv("SNOWFLAKE_AUTHENTICATOR", "snowflake"))
    
    def validate_credentials(self) -> bool:
        """Validate that all required credentials are provided"""
        # For external browser auth, password might not be required
        if self.authenticator == "externalbrowser":
            required_fields = [self.account, self.user]
        else:
            required_fields = [self.account, self.user, self.password]
        return all(field for field in required_fields)
    
    def get_connection_params(self) -> dict:
        """Get connection parameters for snowflake-connector-python"""
        params = {
            'account': self.account,
            'user': self.user,
            'warehouse': self.warehouse,
            'database': self.database,
            'schema': self.schema,
        }
        
        # Add authenticator if specified
        if self.authenticator and self.authenticator != "snowflake":
            params['authenticator'] = self.authenticator
        
        # Add password only if not using external browser auth
        if self.authenticator != "externalbrowser" and self.password:
            params['password'] = self.password
            
        if self.role:
            params['role'] = self.role
            
        return params

class AppConfig(BaseModel):
    """Application configuration"""
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    api_host: str = Field(default_factory=lambda: os.getenv("API_HOST", "localhost"))
    api_port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    
    # External service URLs
    cortex_engine_url: str = Field(default_factory=lambda: os.getenv("CORTEX_ENGINE_URL", "http://localhost:3002"))
    backend_gateway_url: str = Field(default_factory=lambda: os.getenv("BACKEND_GATEWAY_URL", "http://localhost:3003"))

# Global configuration instances
snowflake_config = SnowflakeConfig()
app_config = AppConfig() 