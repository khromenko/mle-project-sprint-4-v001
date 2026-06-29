from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import dotenv
import os
import requests
import pandas as pd
from app import logging_config
from app.model_handler import ModelHandler


'''
Main recomendations service application

run app:
    - uvicorn app.recommendations_service:app --port 8000 # --reload --reload-dir app

'''

logging_config.root_config()
log = logging_config.create_logger(__name__)

ml_model: ModelHandler = None
stats = {}

@asynccontextmanager
async def lifespan_listener(app: FastAPI):
    log.info('app starting (%s)', app)
    
    dotenv.load_dotenv()

    global ml_model
    ml_model = ModelHandler()
    
    # setup .env file
    # ML_MODEL_USER_DATA_PATH = data/recsys/recommendations.parquet
    # ML_MODEL_COMMON_DATA_PATH = data/recsys/top_popular.parquet
    user_data_path = os.getenv('ML_MODEL_USER_DATA_PATH')
    common_data_path = os.getenv('ML_MODEL_COMMON_DATA_PATH')
    
    ml_model.init_model(user_path=user_data_path, user_columns=['user_id', 'item_id', 'rank'],  common_path=common_data_path)

    log.debug('model is loaded')

    yield
    log.info('app stoping:  (%s)', app)

def get_ml_model():
    if(ml_model == None):
        raise(Exception('ml model was not loaded'))
    return ml_model

app = FastAPI(title='Recomendations service', lifespan=lifespan_listener)
log.info('FastApi app started (%s)', app)

@app.post('/get_recommendations_offline')
def get_recommendations_offline(user_id: int, top_k: int = 10, model: ModelHandler = Depends(get_ml_model)):
    '''
    Offline recommendations for user prepared by ml-model
    '''

    log.debug(f'get offline recs for user_id {user_id}, top_k = {top_k}') 

    recs = model.get_recommendations_offline(user_id, top_k)

    if len(recs) == 0:
        _add_stat_counter('offline_recs_empty_query_count')
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        _add_stat_counter('offline_recs_success_query_count')
        return JSONResponse({'recs': recs}, status_code=status.HTTP_200_OK)

@app.post('/get_recommendations_online')
def get_recommendations_online(user_id: int, top_k: int = 10):
    '''
    Online recommendations for user based on user recent history and content service for similar items.
    The result is the top_k of the merged list of 3 recent items top_k similar items sorted by by their score

    '''
    log.debug(f'get online recs for user_id {user_id}, top_k = {top_k}') 

    # 1 - get user recent history
    history_items = _query_user_event_history(user_id, top_k)

    # 2 - get similar items via content service if there is user history
    if len(history_items) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    else:
        sim_items_result = pd.DataFrame(columns=['item_id', 'score'])

        # collect sim items for 3 recent
        for item_id in history_items[:3]:
            sim_items = _query_similar_items(item_id, top_k)
            sim_items_result = pd.concat([sim_items_result, pd.DataFrame(sim_items)])
        
        # take sorted top_k of all items
        sim_items_result = sim_items_result \
            .sort_values(by='score', ascending=False) \
            .reset_index(drop=True) \
            .drop_duplicates(subset='item_id') \
            .head(top_k)
        recs = sim_items_result['item_id'].to_list()
        
        return JSONResponse({'recs': recs}, status_code=status.HTTP_200_OK)

@app.post('/get_recommendations_full')
def get_recommendations_full(user_id: int, top_k: int = 10, model: ModelHandler = Depends(get_ml_model)):
    log.debug(f'get full recs for user_id {user_id}, top_k = {top_k}') 

    recs = model.get_recommendations_offline(user_id, top_k)

    # it is strange if there is no recs - so mark this response as a special 204 code
    if len(recs) == 0:
        _add_stat_counter('full_recs_empty_query_count')
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        _add_stat_counter('full_recs_success_query_count')
        return JSONResponse({'recs': recs}, status_code=status.HTTP_200_OK)


@app.get('/stats')
def get_stats():
    response = stats | ml_model.get_stats()
    return JSONResponse(response)

# ------------------

def _query_user_event_history(user_id, top_k):
    event_store_url='http://localhost:8001/event' 
    params = {
        'user_id': user_id
    }    
    log.debug(f'get user events - url = {event_store_url}, params = {params}')    

    history_items = []

    # 1 - get user recent history
    try:
        response = requests.get(url=event_store_url, params=params)
        resp_status = response.status_code
        
        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            history_items = response.json()["items"]

            if len(history_items) == 0:
                log.debug(f'successfully got empty user events (item ids = {history_items})')
                _add_stat_counter('online_recs_events_query_empty_count')
                
            else:
                log.debug(f'successfully got user events - item ids = {history_items}')
                _add_stat_counter('online_recs_events_query_success_count')

        else:
            _add_stat_counter('online_recs_events_query_fail_count')
            log.error('response reason = %s', response.reason)

    except requests.exceptions.RequestException as e:
        log.error('request for user history exception', exc_info=True)
        _add_stat_counter('online_recs_events_query_error_count')
    
    return history_items

def _query_similar_items(item_id, top_k):
    log.debug(f'get similar items for items_id - {item_id}, top_k = {top_k}') 

    event_store_url='http://localhost:8002/similar' 
    params = {
        'item_id': item_id,
        'top_k': top_k
    }
    
    log.debug(f'query content service - url = {event_store_url}, params = {params}')    

    similar_items = {}
    try:
        response = requests.get(url=event_store_url, params=params)
        resp_status = response.status_code
        
        log.debug('response status = %s', response.status_code)
        log.debug('response data = %s', response.text)
        
        if status.HTTP_200_OK == resp_status:
            similar_items = response.json()

            log.debug(f'successfully got similar items for item ({item_id}) - item ids = {similar_items}')
            _add_stat_counter('online_recs_similar_query_success_count')
                            
        elif status.HTTP_204_NO_CONTENT == resp_status:
            log.debug(f'successfully got empty sim items for item ({item_id}) (item ids = {similar_items})')
            _add_stat_counter('online_recs_similar_query_empty_count')

        else:
            _add_stat_counter('online_recs_similar_query_fail_count')
            log.error('response reason = %s', response.reason)

    except requests.exceptions.RequestException as e:
        log.error('request for user history exception', exc_info=True)
        _add_stat_counter('online_recs_similar_query_error_count')
    
    return similar_items

def _add_stat_counter(name):
    counter = stats[name] if name in stats.keys() else 0
    stats[name] = counter + 1