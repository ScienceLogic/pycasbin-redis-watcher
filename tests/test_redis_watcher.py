import pytest
redis_published_message = ""

@pytest.fixture
def fake_redis(monkeypatch):
    from fakeredis import FakeStrictRedis as Redis

    # publish isn't implemented in FakeRedis:(
    def fake_publish(message):
        redis_published_message = message

    # pubsub.subcsribe isn't timplemented in Fake Redis :(
    class fake_socket():
        def getaddrinfo(host, port, family, type, proto, flags):
            pass

    class fake_pubsub():
        _socket = fake_socket()
        def subscribe(self, channel):
            pass
        def getaddrinfo(self):
            pass
        def execute_command(self):
            pass

    monkeypatch.setattr(Redis, 'publish', fake_publish)
    monkeypatch.setattr(Redis, 'pubsub', fake_pubsub)
    return Redis

@pytest.fixture
def fake_redis_server():
    from fakeredis import FakeServer
    server = FakeServer()
    return server

@pytest.fixture
def redis_watcher(fake_redis, fake_redis_server):
    from casbin_redis_watcher import RedisWatcher
    rw = RedisWatcher(redis_host=fake_redis_server, redis_port=2000,
                      start_process=False)
    return rw

def test_redis_watcher_init(redis_watcher, fake_redis_server):
    assert redis_watcher.redis_url == fake_redis_server
    assert redis_watcher.redis_port == 2000
    assert redis_watcher.parent_conn is not None
    assert redis_watcher.subscribed_process is not None


def test_update(redis_watcher, fake_redis):
    # FakeRedis library does not implement pubsub or publish() or
    # subscribe(). No obvious way to mock this call without undertsanding deep
    # redis pubsub.publish, pubsub._socket, etc. I've maade an attempt but
    # unfortunately was unable to get a full test.
    #import casbin_redis_watcher
    #Redis = fake_redis
    #casbin_redis_watcher.Redis = fake_redis
    #redis_watcher.update()
    #assert redis_watcher.should_reload()
    pass

def test_no_reload(redis_watcher):
    assert not redis_watcher.should_reload()

def test_default_update_callback(redis_watcher):
    assert redis_watcher.update_callback() is None

def test_set_update_callback(redis_watcher):
    def tst_callback():
        pass
    redis_watcher.set_update_callback(tst_callback)
    assert redis_watcher.update_callback == tst_callback

