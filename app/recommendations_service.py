from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import dotenv
import os
from app import logging_config
from app.model_handler import ModelHandler


'''
Main recomendations service application

```bash
 uvicorn app.recommendations_service:app --port 8000 # --reload --reload-dir app
 ```

 '''

logging_config.root_config()
log = logging_config.create_logger(__name__)

ml_model: ModelHandler = None

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
        raise('ml model was not loaded')
    return ml_model

app = FastAPI(title='Recomendations service', lifespan=lifespan_listener)
log.info('FastApi app started (%s)', app)

@app.post('/get_recommendations_full')
def get_recommendations_full(user_id: int, top_k: int = 100, model: ModelHandler = Depends(get_ml_model)):
    log.debug(f'get full recs for user_id {user_id}, top_k = {top_k}') 

    recs = model.get_recommendations_offline(user_id, top_k)

    # it is strange if there is no recs - so mark this response as a special 204 code
    if len(recs) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return JSONResponse({'recs': recs}, status_code=status.HTTP_200_OK)


@app.post('/get_recommendations_offline')
def get_recommendations_offline(user_id: int, top_k: int = 100, model: ModelHandler = Depends(get_ml_model)):
    log.debug(f'get offline recs for user_id {user_id}, top_k = {top_k}') 

    recs = model.get_recommendations_offline(user_id, top_k)

    if len(recs) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return JSONResponse({'recs': recs}, status_code=status.HTTP_200_OK)


@app.post('/get_recommendations_online')
def get_recommendations_online(user_id: int, top_k: int = 100, model: ModelHandler = Depends(get_ml_model)):
    log.debug(f'get online recs for user_id {user_id}, top_k = {top_k}') 

    recs = model.get_recommendations_offline(user_id, top_k)
    
    if len(recs) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return JSONResponse({'recs': recs}, status_code=status.HTTP_200_OK)
