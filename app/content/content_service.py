from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import dotenv
import os
from app import logging_config
from app.content.sim_model_handler import SimModelHandler


'''
Content store service.
Provides similar items.

run app:
    $: uvicorn app.content.content_service:app --port 8002

 '''

logging_config.root_config()
log = logging_config.create_logger(__name__)

sim_ml_model: SimModelHandler = None
stats = {}

@asynccontextmanager
async def lifespan_listener(app: FastAPI):
    log.info('app starting (%s)', app)
    
    dotenv.load_dotenv()

    global sim_ml_model
    sim_ml_model = SimModelHandler()
    
    # setup .env file
    # ML_MODEL_SIM_DATA_PATH = data/recsys/similar.parquet
    data_path = os.getenv('ML_MODEL_SIM_DATA_PATH')
        
    sim_ml_model.init_model(data_path=data_path)

    log.debug('model is loaded')

    yield
    log.info('app stoping:  (%s)', app)

def get_ml_model() -> SimModelHandler:
    if(sim_ml_model == None):
        raise(Exception('sim ml model was not loaded'))
    return sim_ml_model

app = FastAPI(title='Content store service', lifespan=lifespan_listener)

@app.get('/similar')
def get_similar_items(item_id: int, model: SimModelHandler = Depends(get_ml_model)):
    
    sim_items = model.get_similar_items(item_id)

    # it is strange if there is no similar items - so mark this response as a special 204 code
    if len(sim_items) == 0:
        _add_stat_counter('empty_sim_items_query_count')
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    _add_stat_counter('success_sim_items_query_count')
    return JSONResponse({'items': sim_items}, status_code=status.HTTP_200_OK)
    
@app.get('/stats')
def get_stats():
    return JSONResponse(stats)

def _add_stat_counter(name):
    counter = stats[name] if name in stats.keys() else 0
    stats[name] = counter + 1
    