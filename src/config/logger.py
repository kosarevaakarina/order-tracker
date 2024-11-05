import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

def create_handler(file_name, level):
    handler = logging.FileHandler(file_name, encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler

logger.addHandler(create_handler('error.log', logging.ERROR))
logger.addHandler(create_handler('debug.log', logging.DEBUG))
