import logging
from app import logging_config
import numpy as np
import random

logging_config.create_logger(__name__)
log = logging.getLogger(__name__)

class ModelHandler():
    def __init__(self):
        log.info('loading model ..')

    def get_recommendations_offline(self, user_id):
        log.info('get recs for user_id = %s', user_id)

        recs = np.array([1,2,3]) * random.randint(0,100)
        
        return recs.tolist()
    

