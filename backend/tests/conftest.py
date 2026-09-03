import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "real_save: requires a real .sav fixture file")
