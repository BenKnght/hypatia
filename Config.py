import logging

logger = logging.getLogger(__name__)


def setup_logging(filehandler=None):
    # Logging setup
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    if filehandler:
        filehandler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(filehandler)
