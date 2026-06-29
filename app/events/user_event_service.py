from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.events.user_event_store import UserEvent, UserEventStore
from app import logging_config

'''
User events store service

run app:
    $: uvicorn app.events.user_event_service:app --port 8001 # --reload --reload-dir app

 '''

logging_config.root_config()
log = logging_config.create_logger(__name__)

app = FastAPI(title='User event store service')
event_store = UserEventStore()
    
class UserEventPayload(BaseModel):
    user_id: int
    item_id: int

    def make_event(self) -> UserEvent:
        return UserEvent(self.user_id, self.item_id)

@app.post('/event')
def add(event_data: UserEventPayload):
    items = event_store.put(event_data.make_event())
    return JSONResponse({'items': items}, status_code=status.HTTP_200_OK)
     
@app.get('/event')
def get(user_id: int):
    items = event_store.get(user_id)
    return JSONResponse({'items': items}, status_code=status.HTTP_200_OK)

@app.get('/store')
def get_all():
    store = event_store.get_store()
    return JSONResponse(store, status_code=status.HTTP_200_OK)
