from pytest import Parser, FixtureRequest, fixture, skip, mark
import requests
from random import randint
from app import logging_config
from fastapi import status
from fastapi.testclient import TestClient

'''
Test cases for recommendations service application

start main app
    $: uvicorn app.recommendations_service:app --port 8000

run test
    $ python -m pytest test/test_service.py --case=(offline|online|full) -s
'''

log = logging_config.create_logger(__name__)

recsys_url='http://localhost:8000/get_recommendations'

def setup_module():
    pass

def _genereate_user_params():
    params = {
        'user_id': randint(0, 1320000), 
        'top_k': randint(0, 100)
    }    
    return params
    
def test_online(test_case: str):
    if test_case != 'online': skip('skip not "online" test case')

    url = f'{recsys_url}_online'
    params = _genereate_user_params()
    
    log.debug(f'online: params = {params}, url = {url}')
    
    try:
        response = requests.post(url=url, params=params)
        status = response.status_code
        
        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if requests.codes.ok == status:
            log.debug(f'successfully got recs for user (count = {len(response.json()["recs"])})')            
        
        else:
            log.debug('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)

def test_offline(test_case: str):
    if test_case != 'offline': skip('skip not "offline" test case')

    url = f'{recsys_url}_offline'
    params = _genereate_user_params()
    
    log.debug(f'offline: params = {params}, url = {url}')

    try:
        response = requests.post(url=url, params=params)
        resp_status = response.status_code

        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            log.debug(f'successfully got recs for user (count = {len(response.json()["recs"])})')            
        elif status.HTTP_204_NO_CONTENT == resp_status:
            log.warning('alert - no content for user')
        else:
            log.debug('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)

def test_full(test_case: str):
    if test_case != 'full': skip('skip not "full" test case')

    url = f'{recsys_url}_full'
    params = _genereate_user_params()
    
    log.debug(f'full: params = {params}, url = {url}')

    try:
        response = requests.post(url=url, params=params)
        status = response.status_code

        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if requests.codes.ok == status:
            log.debug(f'successfully got recs for user (count = {len(response.json()["recs"])})')            
        else:
            log.debug('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)