"""Tests for the in-memory cache module."""

import time

import pytest

import backend.cache as cache_module


@pytest.fixture(autouse=True)
def clear_cache():
    cache_module.flush_all()
    yield
    cache_module.flush_all()


class TestCacheGetSet:
    def test_set_and_get(self):
        cache_module.set("k1", {"a": 1}, ttl=60)
        assert cache_module.get("k1", ttl=60) == {"a": 1}

    def test_get_missing(self):
        assert cache_module.get("nonexistent", ttl=60) is None

    def test_expiry(self):
        cache_module.set("k2", "value", ttl=60)
        # Manually backdate the entry
        import backend.cache as c
        with c._store_lock:
            c._store["k2"] = ("value", time.time() - 100)
        assert cache_module.get("k2", ttl=60) is None

    def test_delete(self):
        cache_module.set("k3", 42, ttl=60)
        cache_module.delete("k3")
        assert cache_module.get("k3", ttl=60) is None

    def test_flush_all(self):
        cache_module.set("k4", "x", ttl=60)
        cache_module.set("k5", "y", ttl=60)
        cache_module.flush_all()
        assert cache_module.get("k4", ttl=60) is None
        assert cache_module.get("k5", ttl=60) is None


class TestCacheDecorator:
    def test_caches_return_value(self):
        call_count = {"n": 0}

        @cache_module.cache(ttl=60)
        def my_fn(x):
            call_count["n"] += 1
            return x * 2

        result1 = my_fn(5)
        result2 = my_fn(5)
        assert result1 == result2 == 10
        assert call_count["n"] == 1  # only called once

    def test_different_args_not_shared(self):
        call_count = {"n": 0}

        @cache_module.cache(ttl=60)
        def double(x):
            call_count["n"] += 1
            return x * 2

        assert double(3) == 6
        assert double(4) == 8
        assert call_count["n"] == 2


class TestCacheInfo:
    def test_info_returns_dict(self):
        info = cache_module.info()
        assert isinstance(info, dict)
        assert "backend" in info
        assert "connected" in info

    def test_info_backend_memory(self):
        info = cache_module.info()
        # In test env there's no Redis
        assert info["backend"] == "memory"
