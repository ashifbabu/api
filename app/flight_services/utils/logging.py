import logging

def setup_logging():
    """
    Set up the logging configuration for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Logs to console
            logging.FileHandler("app.log"),  # Logs to a file
        ],
    )

    # Example of logging initialization
    logger = logging.getLogger("flight_services")
    logger.setLevel(logging.DEBUG)  # Set default log level
    return logger
