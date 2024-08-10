import os
import pytest

from turbohttp.app import TurboHTTP


@pytest.fixture
def app():
    return TurboHTTP()


@pytest.fixture
def test_client(app):
    return app.test_session()
