import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

def create_handler(file_name, level, filter_error=False):
    handler = logging.FileHandler(file_name, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(formatter)

    if filter_error:
        handler.addFilter(lambda record: record.levelno < logging.ERROR)

    return handler

logger.addHandler(create_handler('error.log', logging.ERROR))
logger.addHandler(create_handler('debug.log', logging.DEBUG, filter_error=True))
