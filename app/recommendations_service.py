from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app import logging_config
from app.model_handler import ModelHandler

'''
Main recomendations service application

$: uvicorn app.recommendations_service:app --port 8000 # --reload --reload-dir app
'''

logging_config.root_config()
log = logging_config.create_logger(__name__)

ml_model: ModelHandler = None

@asynccontextmanager
async def lifespan_listener(app: FastAPI):
    log.info('app starting (%s)', app)
    
    global ml_model
    ml_model = ModelHandler()

    yield
    log.info('app stoping:  (%s)', app)

def get_ml_model():
    if(ml_model == None):
        raise('ml model was not loaded')
    return ml_model

app = FastAPI(title='Recomendations service', lifespan=lifespan_listener)
log.info('FastApi app started (%s)', app)

@app.post('/get_recommendations_full')
def get_recommendations_full(user_id: int, model: ModelHandler = Depends(get_ml_model)):
    log.info('user_id: %s', user_id) 

    recs = model.get_recommendations_offline(user_id)

    return JSONResponse({'recs': recs}, status_code=status.HTTP_200_OK)


@app.post('/get_recommendations_offline')
def get_recommendations_offline(user_id: int, model: ModelHandler = Depends(get_ml_model)):
    log.info('user_id: %s', user_id) 

    recs = model.get_recommendations_offline(user_id)

    return JSONResponse({'recs': [1,2,3]}, status_code=status.HTTP_200_OK)


@app.post('/get_recommendations_online')
def get_recommendations_online(user_id: int, model: ModelHandler = Depends(get_ml_model)):
    log.info('user_id: %s', user_id) 

    recs = model.get_recommendations_offline(user_id)

    return JSONResponse({'recs': [1,2,3]}, status_code=status.HTTP_200_OK)
