import logging

from opencensus.ext.azure.log_exporter import AzureLogHandler
import structlog

from geonames import APP_INSIGHTS_KEY, APP_LOG_KEY, LOG_LEVEL


log_level_code = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(log_level_code, int):
    raise ValueError(f'Invalid log level: {LOG_LEVEL}')

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
root_logger.setLevel(log_level_code)

# Define a standard output Handler
console = logging.StreamHandler()
console.setLevel(log_level_code)
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')
console.setFormatter(formatter)
root_logger.addHandler(console)

# Add and define Azure app insights log handler.
# az_handler = AzureLogHandler(connection_string=f'InstrumentationKey={APP_INSIGHTS_KEY}')
# az_handler.setLevel(log_level_code)
# az_formatter = logging.Formatter('%(message)s')
# az_handler.setFormatter(az_formatter)
# root_logger.addHandler(az_handler)

# Quiet chatty libs
logging.getLogger('azure.core.pipeline.policies').setLevel(logging.ERROR)
logging.getLogger('numba.core').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
# logging.getLogger('msal').setLevel(logging.ERROR)


def get_logger(name):
    """
    This returns a reference to the global logger with a binding.

    :param name: the application name used as a default binding.
    :return: The structlog logger
    """
    return structlog.get_logger(name).bind(source_app=APP_LOG_KEY)