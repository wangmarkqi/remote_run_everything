from functools import wraps
from remote_run_everything.db.kv_store import KvStore


def cache_by_name(k, ts):
    def _wrapper(f):
        wraps(f)

        def _wrapped(*args, **kwargs):
            mykv = KvStore()
            res = mykv.read_with_ex(k, ts)
            if res is None:
                res = f(*args, **kwargs)
                if res is not None:
                    mykv.write_with_ex(k, res)
                return res
            return res

        return _wrapped

    return _wrapper


def cache_by_1starg(sub, ts):
    def _wrapper(f):
        wraps(f)

        def _wrapped(*args, **kwargs):
            mykv = KvStore()
            k = f"{sub}{args[0]}"
            res = mykv.read_with_ex(k, ts)
            if res is None:
                res = f(*args, **kwargs)
                if res is not None:
                    mykv.write_with_ex(k, res)
                return res
            return res

        return _wrapped

    return _wrapper


def cache_by_nth_arg(sub, index, ts):
    def _wrapper(f):
        wraps(f)

        def _wrapped(*args, **kwargs):
            mykv = KvStore()
            k = f"{sub}{args[index]}"
            res = mykv.read_with_ex(k, ts)
            if res is None:
                res = f(*args, **kwargs)
                if res is not None:
                    mykv.write_with_ex(k, res)
                return res
            return res

        return _wrapped

    return _wrapper


def cache_by_rkey(ts):
    def _wrapper(f):
        wraps(f)

        def _wrapped(*args, **kwargs):
            mykv = KvStore()
            k = str(kwargs['rkey'])
            res = mykv.read_with_ex(k, ts)
            if res is None:
                res = f(*args, **kwargs)
                if res is not None:
                    mykv.write_with_ex(k, res)
                return res
            return res

        return _wrapped

    return _wrapper
