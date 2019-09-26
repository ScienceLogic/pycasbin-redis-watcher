from redis import Redis
from flask-casbin import Watcher
from multiprocessing import Process, Pipe
import time

REDIS_CHANNEL_NAME = "casbin-role-watcher"

def redis_casbin_subscription(redis_url, process_conn, redis_port=None):
    r = Redis(redis_url, redis_port)
    p = r.pubsub()
    p.subscribe(REDIS_CHANNEL_NAME)
    print("Waiting for casbin policy updates...")
    while True:
        # wait 20 seconds to see if there is a casbin update
        message = p.get_message(timeout=20)
        if message and message.get('type') == "message":
            print("Casbin policy update identified.."
                  " Message was: {}".format(message))
            process_conn.send(message)



class RedisWatcher(Watcher):

    def __init__(self, redis_host, redis_port=None):
        self.redis_url = redis_host
        self.redis_port = redis_port
        self.parent_conn, child_conn = Pipe()
        self.subscribed_process = Process(target=redis_casbin_subscription,
                                          args=(redis_host, child_conn,
                                                redis_port))
        self.subscribed_process.start()

    def set_update_callback(self, fn):
        self.update_callback = fn

    def update_callback(self):
        print('callback called because casbin role updated')

    def update(self):
        r = Redis(self.redis_url, self.redis_port)
        r.publish(REDIS_CHANNEL_NAME, 'casbin policy'
                                      ' updated at {}'.format(time.time()))

    def should_reload(self):
        try:
            if self.parent_conn.poll():
                message = self.parent_conn.recv()
                return True
        except EOFError:
            print("Child casbin-watcher subscribe prococess has stopped")
            return False