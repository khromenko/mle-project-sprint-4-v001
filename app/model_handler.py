import logging
from app import logging_config
import numpy as np
import random
import pandas as pd

'''
ML-model handler for offline recommendations.

Usage:
    - init_model() to load recomendations data
    - get_recommendations_offline() - to get recomendations for user
'''

log = logging_config.create_logger(__name__)

class ModelHandler():
    def __init__(self):
        log.debug('create model handler')

        self.user_recs = None
        self.common_recs = None
        self.stats = {}

    def _add_stat_counter(self, name):
        counter = self.stats[name] if name in self.stats.keys() else 0
        self.stats[name] = counter + 1

    def _init_user_recs(self, user_path, columns):
        try:
            self.user_recs = pd.read_parquet(user_path, columns=columns)
            self.user_recs = self.user_recs.set_index('user_id')

            log.debug(f'user recs data loaded: \n{self.user_recs}')

        except Exception as e:
            log.error('user data load error', exc_info=True)           
            self.user_recs = None

    def _init_common_recs(self, common_path):
        try:
            self.common_recs = pd.read_parquet(common_path)

            log.debug(f'common recs data loaded: \n{self.common_recs}')

        except Exception as e:
            log.error('common recs data load error', exc_info=True)
            self.common_recs = None

    def init_model(self, user_path, user_columns, common_path):
        '''
        Prediction model initialization
        Args
            - user_path - data path for personal recommendations
            - common_path - data path for common recommendations, as a fallback for empty personal recommendations
        '''
        
        log.info(f'user path = {user_path}, common path: {common_path}, user_columns = {user_columns}')

        self._init_user_recs(user_path, user_columns)                    
        self._init_common_recs(common_path) 

    def get_recommendations_offline(self, user_id: int, top_k: int = 100):
        log.debug(f'get recs for user_id = {user_id}, top_k = {top_k}')

        recs = []
        if self.user_recs is not None:
            try:
                recs = self.user_recs.loc[user_id]['item_id'][:top_k].tolist()
                self._add_stat_counter('offline_recs_model_success_count')
            except KeyError as e:
                log.info(f'there is no personal recs for user = {user_id} - fallback to common recs')
                self._add_stat_counter('offline_recs_model_empty_user_count')
                recs = []
            except Exception as e:
                self._add_stat_counter('offline_recs_model_error_user_count')
                log.error('error getting user personal recs - fallback to common recs', exc_info=True)
                recs = []
        else:
            self._add_stat_counter('offline_recs_model_fail_user_count')
            log.warning(f'alert - user recs is not loaded')
        
        # no personal recs was found - use common recs for this user
        if len(recs) == 0:
            if self.common_recs is not None:
                try:
                    recs = self.common_recs[:top_k].index.tolist()
                    self._add_stat_counter('offline_recs_model_success_common_count')
                except Exception as e:
                    log.error('error getting common recs', exc_info=True)
                    self._add_stat_counter('offline_recs_model_error_common_count')
                    recs = []
            else:
                self._add_stat_counter('offline_recs_model_fail_common_count')
                log.warning(f'alert - common recs is not loaded')
        
        return recs
    
    def get_stats(self):
        return self.stats
