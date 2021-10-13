import os

from qtask.config import config


def setup_data_dirs():
    os.makedirs(config["QTASK_DATA_DIR"], exist_ok=True)
