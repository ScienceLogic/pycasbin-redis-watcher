# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pip install -r requirements.txt
pip install -r dev_requirements.txt
```

## Tests

```bash
pytest tests/                                              # all tests
pytest tests/test_redis_watcher.py::test_redis_watcher_init  # single test
```

No tox, Makefile, or CI configuration exists in this repo.

## Architecture

This is a small, single-purpose library: a [pycasbin](https://github.com/casbin/pycasbin) watcher that propagates policy updates across distributed processes via Redis pub/sub.

**Channel**: all messages use the hardcoded channel `"casbin-role-watcher"`.

**Two-process design** (`casbin_redis_watcher/watcher.py`):

- `RedisWatcher` (main process) — holds a `multiprocessing.Pipe` parent end; exposes `update()`, `should_reload()`, and `set_update_callback()`.
- `redis_casbin_subscription()` (daemon subprocess) — subscribes to the Redis channel, polls every 20 seconds (`get_message(timeout=20)`), and sends any received messages back through the Pipe child end.

**Policy reload flow**:
1. Any process calls `watcher.update()` → publishes a timestamped message to Redis.
2. The subscriber daemon receives it and sends it through the Pipe.
3. The caller (e.g., a Flask/uWSGI worker) periodically calls `watcher.should_reload()`, which polls the Pipe; returns `True` when a message is present.
4. The registered `update_callback` (typically `enforcer.load_policy`) reloads the policy.

**uWSGI note**: because the subprocess is spawned in `__init__`, it must be created *after* uWSGI forks workers (`@postfork`). See README for the pattern.

**Error recovery**: if the subscriber process dies (pipe raises `EOFError`), `should_reload()` automatically recreates it with a 10-second delay.
