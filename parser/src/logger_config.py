"""
Logger configuration for the milon parser project.

Default behavior:
- Console: INFO, WARNING, ERROR
- File: ALL levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

To enable DEBUG on console:
- Set environment variable: PARSER_DEBUG=1
- Or call: setup_logging(debug=True)
"""

import logging
import os


def setup_logging(debug=None, log_file="parser.log"):
    """
    Configure logging for the project.

    Args:
        debug (bool, optional): Enable DEBUG level on console.
                               If None, checks PARSER_DEBUG environment variable.
        log_file (str): Path to log file. Default: "parser.log"
                       File is overwritten on each run.

    Returns:
        logging.Logger: The root logger
    """
    # Determine debug level
    if debug is None:
        debug = os.getenv('PARSER_DEBUG', '0') == '1'

    console_level = logging.DEBUG if debug else logging.INFO

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels

    # Remove any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler (INFO or DEBUG based on setting)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (ALL levels, overwrite on each run)
    file_handler = logging.FileHandler(
        log_file,
        mode='w',  # Overwrite file on each run
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name):
    """
    Get a logger instance for a module.

    Args:
        name (str): Name of the logger (typically __name__)

    Returns:
        logging.Logger: Logger instance

    Example:
        logger = get_logger(__name__)
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()
