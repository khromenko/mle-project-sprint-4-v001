from pytest import Parser, FixtureRequest, fixture, skip, mark
import requests
from random import randint, choice
from app import logging_config
from fastapi import status
from fastapi.testclient import TestClient

'''
Test cases for contents service

start content service
    uvicorn app.content.content_service:app --port 8002

run test
    python -m pytest test/test_content_service.py -s
'''

log = logging_config.create_logger(__name__)

service_url='http://localhost:8002'

def setup_module():
    pass

def test_get_sim_items():
    
    url = f'{service_url}/similar'

    # random 10 items sample
    sample_item_ids = [43854569, 55307683, 21692972, 92255425, 28259199, 31430656, 41666510, 32859902, 24001400, 80091826]
    
    for i in range(0,10):
        if i % 2 == 0:
            item_id = choice(sample_item_ids)
        else:
            item_id = randint(0, 1000000)

        params = {
            'item_id': item_id,
            'top_k': randint(1,10)
        }
        _exec_get_sim_items(params)
    
def test_stats():
    url = f'{service_url}/stats'

    log.debug(f'get stats - url = {url}')
    
    try:
        response = requests.get(url=url)
        resp_status = response.status_code

        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            log.debug(f'successfully got stats')

        else:
            log.error('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)

def _exec_get_sim_items(params):
    
    url = f'{service_url}/similar'

    log.debug(f'get sim items - url = {url}, params = {params}')

    try:
        response = requests.get(url=url, params=params)
        resp_status = response.status_code

        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            log.debug(f'successfully got sim items for item ({params["item_id"]}) = {response.json()})')            

        elif status.HTTP_204_NO_CONTENT == resp_status:
            log.warning('alert - no content for item')
        else:
            log.error('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)