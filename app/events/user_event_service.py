from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.events.user_event_store import UserEvent, UserEventStore
from app import logging_config

'''
User events store service

run app:
    $: uvicorn app.events.user_event_service:app --port 8001

 '''

logging_config.root_config()
log = logging_config.create_logger(__name__)

app = FastAPI(title='User event store service')
event_store = UserEventStore()
stats = {}
    
class UserEventPayload(BaseModel):
    user_id: int
    item_id: int

    def make_event(self) -> UserEvent:
        return UserEvent(self.user_id, self.item_id)

@app.post('/event')
def add(event_data: UserEventPayload):
    items = event_store.put(event_data.make_event())

    _add_stat_counter('user_event_add_count')

    return JSONResponse({'items': items}, status_code=status.HTTP_200_OK)
     
@app.get('/event')
def get(user_id: int):
    items = event_store.get(user_id)

    _add_stat_counter('user_id_query_count')

    return JSONResponse({'items': items}, status_code=status.HTTP_200_OK)

@app.get('/store')
def get_all():
    store = event_store.get_store()
    
    _add_stat_counter('all_store_query_count')

    return JSONResponse(store, status_code=status.HTTP_200_OK)

@app.get('/stats')
def get_stats():
    return JSONResponse(stats)

def _add_stat_counter(name):
    counter = stats[name] if name in stats.keys() else 0
    stats[name] = counter + 1