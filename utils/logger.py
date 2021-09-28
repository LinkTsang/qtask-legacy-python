import logging
from os.path import join as pjoin

from config import QTASK_LOG_FILE_NAME


def setup_logger(log_dir='./logs'):
    logging.basicConfig(
        filename=pjoin(log_dir, QTASK_LOG_FILE_NAME),
        level=logging.DEBUG,
        format='%(asctime)-15s %(levelname)s %(name)s %(message)s')
