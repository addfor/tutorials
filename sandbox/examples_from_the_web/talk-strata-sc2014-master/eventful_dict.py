import time

class EventfulDict(dict):
    """Eventful dictionary"""

    def __init__(self, *args, **kwargs):
        """Sleep is an optional float that allows you to tell the
        dictionary to hang for the given amount of seconds on each
        event.  This is usefull for animations."""
        self._sleep = kwargs.get('sleep', 0.0)
        self._add_callbacks = []
        self._del_callbacks = []
        self._set_callbacks = []
        dict.__init__(self, *args, **kwargs)
        
    def on_add(self, callback, remove=False):
        self._register_callback(self._add_callbacks, callback, remove)
    def on_del(self, callback, remove=False):
        self._register_callback(self._del_callbacks, callback, remove)
    def on_set(self, callback, remove=False):
        self._register_callback(self._set_callbacks, callback, remove)
    def _register_callback(self, callback_list, callback, remove=False):
        if callable(callback):
            if remove and callback in callback_list:
                callback_list.remove(callback)
            elif not remove and not callback in callback_list:
                callback_list.append(callback)
        else:
            raise Exception('Callback must be callable.')

    def _handle_add(self, key, value):
        self._try_callbacks(self._add_callbacks, key, value)
        self._try_sleep()
    def _handle_del(self, key):
        self._try_callbacks(self._del_callbacks, key)
        self._try_sleep()
    def _handle_set(self, key, value):
        self._try_callbacks(self._set_callbacks, key, value)
        self._try_sleep()
    def _try_callbacks(self, callback_list, *pargs, **kwargs):
        for callback in callback_list:
            callback(*pargs, **kwargs)
            
    def _try_sleep(self):
        if self._sleep > 0.0:
            time.sleep(self._sleep)
    
    def __setitem__(self, key, value):
        return_val = None
        exists = False
        if key in self:
            exists = True
            
        # If the user sets the property to a new dict, make the dict
        # eventful and listen to the changes of it ONLY if it is not
        # already eventful.  Any modification to this new dict will
        # fire a set event of the parent dict.
        if isinstance(value, dict) and not isinstance(value, EventfulDict):
            new_dict = EventfulDict(value)
            
            def handle_change(*pargs, **kwargs):
                self._try_callbacks(self._set_callbacks, key, dict.__getitem__(self, key))
                
            new_dict.on_add(handle_change)
            new_dict.on_del(handle_change)
            new_dict.on_set(handle_change)
            return_val = dict.__setitem__(self, key, new_dict)
        else:
            return_val = dict.__setitem__(self, key, value)
        
        if exists:
            self._handle_set(key, value)
        else:
            self._handle_add(key, value)
        return return_val
        
    def __delitem__(self, key):
        return_val = dict.__delitem__(self, key)
        self._handle_del(key)
        return return_val

    def pop(self, key):
        return_val = dict.pop(self, key)
        if key in self:
            self._handle_del(key)
        return return_val

    def popitem(self):
        popped = dict.popitem(self)
        if popped is not None and popped[0] is not None:
            self._handle_del(popped[0])
        return popped

    def update(self, other_dict):
        for (key, value) in other_dict.items():
            self[key] = value
            
    def clear(self):
        for key in list(self.keys()):
            del self[key]