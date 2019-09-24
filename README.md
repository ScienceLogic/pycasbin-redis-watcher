# Flask-Casbin-Redis-Watcher

Casbin role watcher to be used for monitoring updates to casbin policies

### Installation
```
pip install flask-casbin-redis-watcher
```

### Basic Usage
```
from flask_casbin import CasbinEnforcer
from flask_casbin_redis_watcher import RedisWatcher
casbin_enforcer = CasbinEnforcer(app, adapter)
watcher=RedisWatcher(redis_hostname, redis_port)
watcher.set_update_callback(casbin_enforcer.e.load_policy)
casbin_enforcer.set_watcher(watcher)

```
