import logging
import os


def setup_logging(log_path: str = "data_riot/log/data_pipeline.log") -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    logger.handlers.clear()

    # File handler (INFO+)
    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setLevel(logging.INFO)

    # Console handler (DEBUG+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)