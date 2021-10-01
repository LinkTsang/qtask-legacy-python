import os

from config import QTASK_DEFAULT_DATA_DIR


def setup_data_dirs():
    os.makedirs(QTASK_DEFAULT_DATA_DIR, exist_ok=True)
