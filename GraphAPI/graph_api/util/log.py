import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler
import structlog

from graph_api import APP_INSIGHTS_KEY, APP_IDENTIFIER

# Equivalent to:
# util.basicConfig(format='%(asctime)s %(levelname)s [%(name)s]: %(message)s',
#                     datefmt='%Y-%m-%d %I:%M:%S %p', level=util.INFO)

# Structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # structlog.stdlib.render_to_log_kwargs,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
        structlog.processors.JSONRenderer(indent=2),
        # structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

root_logger = logging.getLogger(name=None)
root_logger.setLevel(logging.DEBUG)

# Define a standard output Handler
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')
console.setFormatter(formatter)
root_logger.addHandler(console)

# Define Azure app insights log handler.
az_handler = AzureLogHandler(connection_string=f'InstrumentationKey={APP_INSIGHTS_KEY}')
az_handler.setLevel(logging.DEBUG)
az_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')
az_handler.setFormatter(az_formatter)

# Add Azure app insights logging.
root_logger.addHandler(az_handler)

# Quiet chatty libs
logging.getLogger('azure.core.pipeline.policies').setLevel(logging.ERROR)

# Global logger
logger = structlog.get_logger().bind(source_app=APP_IDENTIFIER)
