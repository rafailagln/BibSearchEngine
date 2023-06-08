import logging


class MyLogger:
    def __init__(self, log_level=logging.DEBUG):
        self.log_level = log_level
        self.logger = self._configure_logger()

    def _configure_logger(self):
        logger = logging.getLogger(__name__)

        # Check if the logger has handlers already (which would be the case if it was already instantiated)
        if not logger.handlers:
            logger.setLevel(self.log_level)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(self.log_level)
            stream_handler.setFormatter(formatter)

            logger.addHandler(stream_handler)

        return logger

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)
