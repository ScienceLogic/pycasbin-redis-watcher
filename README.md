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

### Using alongside UWSGI 
This redis-watcher module starts separate processes which subscribe to a redis channel, and listens for updates to the casbin policy on that channel. When running within WSGI contexts (like uwsgi) you may want to start these processes as a postfork action. As is depicted below:
```
try:
    from uwsgidecorators import postfork
    print("Running in uwsgi context")
except ModuleNotFoundError:
    print("Not running in uwsgi context")
    postfork = None

if postfork:
    @postfork
    def load_watcher():
        global casbin_enforcer
        watcher = RedisWatcher(redis_info.hostname, redis_info.port)
        watcher.set_update_callback(casbin_enforcer.e.load_policy)
        casbin_enforcer.set_watcher(watcher)

```
