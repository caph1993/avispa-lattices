import functools
import weakref
from typing import Any, Callable, Optional, Type, TypeVar, Union, cast
from typing_extensions import Protocol
from typing import Callable, TypeVar, Generic
# Cached property both in library and in object

_T = TypeVar('_T')
#import cp93pytools.methodtools


class _Property(Protocol[_T]):
    __get__: Callable[..., _T]


class _NormalMethod(Protocol[_T]):
    __name__: str
    __call__: Callable[..., _T]


def cached_method(maxsize=128, typed=False):
    '''decorator for converting a method into an lru cached method'''

    # https://stackoverflow.com/a/33672499/3671939
    def decorator(func: _NormalMethod[_T]) -> _NormalMethod[_T]:

        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            weak_self = weakref.ref(self)

            @functools.wraps(func)
            @functools.lru_cache(maxsize=maxsize, typed=typed)
            def _cached_method(*args, **kwargs):
                self = weak_self()
                assert self
                return func(self, *args, **kwargs)

            setattr(self, func.__name__, _cached_method)
            return _cached_method(*args, **kwargs)

        return wrapped_func

    return decorator


class cached_property(property, _Property[_T]):
    '''
    decorator for converting a method into a cached property
    See https://stackoverflow.com/a/4037979/3671939
    This uses a modification:
    1. inherit from property, which disables setattr(instance, name, value)
        as it raises AttributeError: Can't set attribute
    2. use instance.__dict__[name] = value to fix
    '''

    def __init__(self, method: Callable[..., _T]):
        self._method = method

    def __get__(self, instance, _) -> _T:
        name = self._method.__name__
        value = self._method(instance)
        instance.__dict__[name] = value
        return value

    # def delete(self, instance, property_name: str):
    #     del instance.__dict__[property_name]

    @classmethod
    def set_property(cls, instance, property_name: str, value):
        instance.__dict__[property_name] = value

    @classmethod
    def is_computed(cls, instance, property_name: str):
        return property_name in instance.__dict__


class globally_cached_property(cached_property[_T]):
    '''
    decorator for converting a method into a cached property
    See https://stackoverflow.com/a/4037979/3671939
    This uses a modification:
    1. inherit from property, which disables setattr(instance, name, value)
        as it raises AttributeError: Can't set attribute
    2. use instance.__dict__[name] = value to fix
    '''
    cache = {}

    def __get__(self, instance, _) -> _T:
        name = self._method.__name__
        try:
            value = self.cache[(name, instance)]
        except KeyError:
            value = self._method(instance)
            self.cache[(name, instance)] = value
        instance.__dict__[name] = value
        return value

    def set_property(self, instance, property_name: str, value):
        instance.__dict__[property_name] = value
        self.cache[(property_name, instance)] = value
