from logging import getLogger
from logging.config import dictConfig

from project_logs.config import config


def set_logging(file_name):
    _file_name = f"project_logs/logs/{file_name}"
    log_config = config({"filename": _file_name})
    dictConfig(log_config)
    auxLogger = getLogger(
        _file_name,
    )
    auxLogger.disabled = False
    return auxLogger
