# pycasbin redis watcher

Casbin role watcher to be used for monitoring updates to casbin policies

### Installation
```
pip install pycasbin-redis-watcher
```

### Basic Usage
Example used along with https://github.com/pycasbin/flask-authz
```
from flask_authz import CasbinEnforcer
from casbin_redis_watcher import RedisWatcher
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
