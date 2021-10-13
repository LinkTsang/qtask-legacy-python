import logging
from os.path import join as pjoin

from qtask.config import config


def setup_logger(log_dir=config['QTASK_LOGS_DIR']):
    logging.basicConfig(
        filename=pjoin(log_dir, config['QTASK_LOG_FILE_NAME']),
        level=logging.DEBUG,
        format='%(asctime)-15s %(levelname)s %(name)s %(message)s')
