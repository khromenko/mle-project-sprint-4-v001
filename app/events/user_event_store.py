from app import logging_config

'''
User events store utilitys
'''

log = logging_config.create_logger(__name__)

class UserEvent:
    user_id: int
    item_id: int

    def __init__(self, user_id: int, item_id: int):
        self.user_id = user_id
        self.item_id = item_id    

class UserEventStore:
    '''
    Online store for user-2-item interaction events
    '''
    def __init__(self):
        self.event_store = {}
        pass    

    def put(self, event: UserEvent):
        '''
        Add online user-2-item interaction event
        '''        
        user_id = event.user_id
        item_id = event.item_id

        log.debug(f'put event - user_id = {user_id}, item_id = {item_id}')
        
        user_items = self.event_store[user_id] if user_id in self.event_store.keys() else []
        user_items.insert(0, item_id)
        
        self.event_store[user_id] = user_items

        log.debug(f'user ({user_id}) items = {user_items}')

        return user_items

    def get(self, user_id: int):
        return self.event_store[user_id]
    
    def get_store(self):
        return self.event_store