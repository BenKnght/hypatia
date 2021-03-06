import logging, sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def setup_logging(filehandler=None):
    # Logging setup
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    if filehandler:
        filehandler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(filehandler)
