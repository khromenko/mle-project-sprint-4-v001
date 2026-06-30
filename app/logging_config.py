import logging
from logging import FileHandler, StreamHandler, Handler
import os
import sys

'''
Configure common logging framework
'''

LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
DATE_FORMAT = '%d.%m.%y %H:%M:%S'

def root_config():
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            #StreamHandler(sys.stdout), # no need to duplicate console output
            FileHandler(filename=f'{LOG_DIR}/app.log', mode='a')
            ],
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        force=True #rewrite pytest or other defaults
    )

def create_logger(logger_name: str):
    
    logger = logging.getLogger(logger_name)
    
    # propagate to commaon log file app.log
    logger.propagate = True

    if not logger.handlers:
        formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

        file_handler = logging.FileHandler(f'{LOG_DIR}/{logger_name}.log')
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Комментарий ревьюера
# Создал универсальную конфигурацию с форматированием, записью в файл и выводом в консоль. 