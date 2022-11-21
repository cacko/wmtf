from wmtf.cli import cli, validate_credentials
from wmtf.config import app_config

try:
    if not app_config.is_configured():
        assert(validate_credentials())    
    cli()
except AssertionError:
    pass