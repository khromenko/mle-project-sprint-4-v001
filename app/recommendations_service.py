from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app import logging_config

'''
Main recomendations service application

$: uvicorn app.recommendations_service:app --port 8000 # --reload --reload-dir app
'''

logging_config.config(__name__)
log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan_listener(app: FastAPI):
    log.info('app starting (%s)', app)
    
    yield
    log.info('app stoping:  (%s)', app)
    

app = FastAPI(title='Recomendations service', lifespan=lifespan_listener)
log.info('FastApi app started (%s)', app)

@app.post('/get_recommendations_full')
def get_recommendations_full(user_id: int):
    log.info('user_id: %s', user_id) 

    return JSONResponse({'recs': [1,2,3]}, status_code=status.HTTP_200_OK)


@app.post('/get_recommendations_offline')
def get_recommendations_offline(user_id: int):
    log.info('user_id: %s', user_id) 

    return JSONResponse({'recs': [1,2,3]}, status_code=status.HTTP_200_OK)


@app.post('/get_recommendations_online')
def get_recommendations_online(user_id: int):
    log.info('user_id: %s', user_id) 

    return JSONResponse({'recs': [1,2,3]}, status_code=status.HTTP_200_OK)
