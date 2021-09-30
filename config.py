from os.path import join as pjoin

QTASK_APP_NAME = 'qtask'
QTASK_DEFAULT_DATA_DIR = 'data'
QTASK_DATABASE_URL = pjoin(f'sqlite:///./{QTASK_DEFAULT_DATA_DIR}/{QTASK_APP_NAME}.sqlite')
QTASK_LOG_FILE_NAME = 'qtask.log'
