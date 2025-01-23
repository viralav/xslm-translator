import logging
from datetime import datetime, timezone

def configure_logger(log_level='INFO', log_file_path=None):
  """
  Configures a Python logger with the specified log level and optional file output.

  Args:
    log_level: The logging level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). 
                Defaults to 'INFO'.
    log_file_path: Optional path to the log file. If None, logs to console only.

  Returns:
    The configured logger object.
  """

  logger = logging.getLogger(__name__)
  logger.setLevel(log_level)

  # Default message format
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # Create console handler
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)

  # Create file handler if log_file_path is provided
  if log_file_path:
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

  return logger


date = datetime.now(timezone.utc)
date_string = f"{date.year}-{date.month}-{date.day}"
log_file = f'{date_string}-translate_app.log'
logger = configure_logger(log_level='DEBUG', log_file_path=log_file) 