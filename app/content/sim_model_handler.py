from app import logging_config
import numpy as np
import random
import pandas as pd

'''
ML-model handler for similar items

Usage:
    - init_model() to load similar items data
    - get_similar_items() - to get similar items for requested item
'''
# Комментарий ревьюера
# Почти каждый модуль и метод имеет docstring с описанием назначения, аргументов и примеров запуска. Похвально!


log = logging_config.create_logger(__name__)

class SimModelHandler():
    def __init__(self):
        log.debug('create SimModelHandler')

        self.similar_items = None
        
    def init_model(self, data_path):
        '''
        Similar items model initialization
        Args
            - data_path - data path for similar items dataset            
        '''
        
        log.info(f'data_path = {data_path}')

        try:
            df = pd.read_parquet(data_path)
            self.similar_items = df.set_index('item_id')
            
            log.debug(f'sim items data loaded: \n{self.similar_items}')
        
        except Exception as e:
            log.error('data load error', exc_info=True)
            self.similar_items = None

        
    def get_similar_items(self, item_id: int, top_k: int = 100):
        log.debug(f'get similar items for item_id = {item_id}, top_k = {top_k}')

        items = {"item_id": [], "score": []}
        if self.similar_items is not None:
            try:
                items = self.similar_items \
                    .loc[item_id] \
                    .head(top_k) \
                    .rename(columns={'sim_item_id': 'item_id'}) \
                    .to_dict(orient='list')
                
                items["score"] = [round(x, 5) for x in items["score"]]

            # Комментарий ревьюера
            # Лучше проверить наличие колонок.
            
            except KeyError as e:
                log.warning(f'alert - there is no similar items for item = {item_id}')                
        else:
            log.warning(f'alert - sim items data is not loaded')
                
        return items
    

