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

    # random 100 items sample from df
    item_ids = [43854569, 55307683, 21692972, 92255425, 28259199, 31430656, 41666510, 32859902, 24001400, 80091826, 79304381, 89338829, 83003106, 73301065, 41545342, 46381778, 65671, 62548896, 83216045, 40320, 34252272, 27120924, 31632176, 42994889, 76887365, 168577, 91885580, 26468135, 29238736, 68390256, 84198552, 41455803, 953432, 48591660, 769804, 34391884, 68341113, 65954354, 57763723, 44939863, 28472737, 63280844, 41684287, 364514, 64378100, 35006177, 80251, 41496884, 90464639, 80932860, 23264755, 74823470, 50001852, 20759641, 14271951, 20454357, 1770878, 20164939, 24800538, 64415853, 869320, 325854, 37686419, 33390323, 39512096, 46562522, 55556700, 72398768, 34351858, 91356405, 15359399, 9293174, 99552414, 92239860, 632168, 20791881, 655624, 71960213, 38585225, 662061, 8415953, 534241, 68938513, 47709141, 17696326, 79583360, 35429532, 66928319, 23571021, 79142567, 25949283, 375935, 33821501, 45496690, 58477299, 40628929, 5388145, 4071271, 8787440, 52479101]
    
    for i in range(0,10):
        if i % 2 == 0:
            item_id = choice(item_ids)
        else:
            item_id = randint(0, 1000000)

        params = {
            'item_id': item_id,
            'top_k': randint(1,100)
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