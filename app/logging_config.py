import logging
from logging import FileHandler, StreamHandler
import os
import sys

'''
Configure common logging framework
'''

os.makedirs('logs', exist_ok=True)

def config(logger_name: str):
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            StreamHandler(sys.stdout),
            FileHandler(filename=f'logs/{logger_name}.log', mode='a')
            ],
        format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%d.%m.%y %H:%M:%S',
        force=True #rewrite pytest defaults
    )