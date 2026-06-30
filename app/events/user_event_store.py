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
# Комментарий ревьюера
# Ok

    '''
    Online store for user-2-item interaction events.
    The most recent events are added to the head of the list
    '''
    def __init__(self):
        self.event_store = {}
        log.debug('User event store init done')

    def put(self, event: UserEvent):
    # Комментарий ревьюера
    # Пока нормально, но в будущем лучше использовать collections.deque с ограничением размера или хранить события в БД с временными метками.

        '''
        Add online user-2-item interaction event
        '''        
        user_id = event.user_id
        item_id = event.item_id

        log.debug(f'put event - user_id = {user_id}, item_id = {item_id}')
        
        user_items = self.event_store[user_id] if user_id in self.event_store.keys() else []

        # if the same item already exists replace it to be at the begining
        if user_items.count(item_id) > 0:
            user_items.remove(item_id)
        
        user_items.insert(0, item_id)
        
        self.event_store[user_id] = user_items

        log.debug(f'event added: user_id = {user_id}, items = {user_items}')

        return user_items[:10]

    def get(self, user_id: int, recent_n: int = 3):
        user_items = self.event_store[user_id] if user_id in self.event_store.keys() else []
        return user_items[0:recent_n]
    
    def get_store(self):
        return self.event_store