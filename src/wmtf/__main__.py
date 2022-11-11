from wmtf.cli import cli, validate_credentials
from wmtf.config import app_config

try:
    if app_config.is_new:
        assert(validate_credentials())    
    cli()
except AssertionError:
    pass