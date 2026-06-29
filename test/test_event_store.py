from pytest import Parser, FixtureRequest, fixture, skip, mark
import requests
from random import randint
from app import logging_config
from app.events.user_event_service import UserEventPayload
from fastapi import status
from fastapi.testclient import TestClient

'''
Test cases for user event store service

start event store service
    uvicorn app.events.user_event_service:app --port 8001

run test
    python -m pytest test/test_event_store.py -s
'''

log = logging_config.create_logger(__name__)

event_store_url='http://localhost:8001'

def setup_module():
    pass

def _genereate_user_event():
    params = {
        'user_id': randint(0, 10),  #randint(0, 1320000), 
        'item_id': randint(0, 10) #randint(0, 930000)
    }    
    return params

def test_add_user_event():
    url = f'{event_store_url}/event'
    payload = _genereate_user_event()

    log.debug(f'add user event - url = {url}, payload = {payload}')

    try:
        response = requests.post(url=url, json=payload)
        resp_status = response.status_code
        
        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            log.debug(f'successfully got events - item ids = {list(response.json()["items"])})')            
        
        else:
            log.debug('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)

def test_get_user_events():
    url = f'{event_store_url}/event'
    user_id = randint(0, 10)
    params = {
        'user_id': user_id
    }
    
    log.debug(f'get user events - url = {url}, params = {params}')
    
    try:
        response = requests.get(url=url, params=params)
        resp_status = response.status_code
        
        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            log.debug(f'successfully got user events - item ids = {response.json()["items"]})')            
        
        else:
            log.error('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)

def test_get_store():
    url = f'{event_store_url}/store'
        
    log.debug(f'get all events (store) - url = {url}')
    
    try:
        response = requests.get(url=url)
        resp_status = response.status_code
        
        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            log.debug(f'successfully got events store = {response.json()})')            
        
        else:
            log.error('response reason = %s', response.reason)

    except requests.exceptions.ConnectionError as e:
        log.error('fail to connect to running service - %s', e)

def test_stats():
    url = f'{event_store_url}/stats'

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