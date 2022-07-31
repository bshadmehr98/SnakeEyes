from blinker import Namespace
from flask import current_app

my_signals = Namespace()
registry = {}


def get_signal(signal_name):
    if signal_name not in registry:
        registry[signal_name] = my_signals.signal(signal_name)
    return registry[signal_name]


def connect_signal(signal_name):
    def decorator(function):
        get_signal(signal_name).connect(function)
        return function

    return decorator


def register_signals(signals):
    for s in signals:
        get_signal(s)
