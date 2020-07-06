from redis import Redis
from multiprocessing import Process, Pipe
import time

REDIS_CHANNEL_NAME = "casbin-role-watcher"

def redis_casbin_subscription(redis_url, process_conn, redis_port=None,
                              delay=0):
    # in case we want to delay connecting to redis (redis connection failure)
    time.sleep(delay)
    r = Redis(redis_url, redis_port)
    p = r.pubsub()
    p.subscribe(REDIS_CHANNEL_NAME)
    print("Waiting for casbin policy updates...")
    while True and r:
        # wait 20 seconds to see if there is a casbin update
        try:
            message = p.get_message(timeout=20)
        except Exception as e:
            print("Casbin watcher failed to get message from redis due to: {}"
                  .format(repr(e)))
            p.close()
            r = None
            break

        if message and message.get('type') == "message":
            print("Casbin policy update identified.."
                  " Message was: {}".format(message))
            try:
                process_conn.send(message)
            except Exception as e:
                print("Casbin watcher failed sending update to piped"
                      " process due to: {}".format(repr(e)))
                p.close()
                r = None
                break


class RedisWatcher(object):
    def __init__(self, redis_host, redis_port=None, start_process=True):
        self.redis_url = redis_host
        self.redis_port = redis_port
        self.subscribed_process, self.parent_conn = \
            self.create_subscriber_process(start_process)

    def create_subscriber_process(self, start_process=True, delay=0):
        parent_conn, child_conn = Pipe()
        p = Process(target=redis_casbin_subscription,
                    args=(self.redis_url, child_conn, self.redis_port, delay),
                    daemon=True)
        if start_process:
            p.start()
        return p, parent_conn

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
            print("Child casbin-watcher subscribe prococess has stopped, "
                  "attempting to recreate the process in 10 seconds...")
            self.subscribed_process, self.parent_conn = \
                self.create_subscriber_process(delay=10)
            return False