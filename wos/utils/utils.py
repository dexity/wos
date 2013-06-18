from django.core.cache import get_cache, DEFAULT_CACHE_ALIAS
import cPickle as pickle
import base64
from functools import wraps

def cache_function(timeout=10800, backend=DEFAULT_CACHE_ALIAS):
    "Decorator for local memory caching. Used mostly for database wrappers"
    
    def check_cache(f):
        def _check_cache(*args, **kwargs):
            key = pickle.dumps((f.__name__, args, kwargs))
            key = base64.b64encode(key)
            
            fcache   = get_cache(backend)
            if fcache.get(key):
                return fcache.get(key)
            
            value = f(*args, **kwargs)
            fcache.set(key, value, timeout)
            return  value
        return wraps(f)(_check_cache)
    return check_cache  