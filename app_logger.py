import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)s: %(levelname)s %(message)s')


def get_logger(name: str):
    return logging.getLogger(name)

