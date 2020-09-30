import functools

import pytest
from decorator import decorator
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture(scope='module')
def flask_app():
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def client(flask_app):
    app = flask_app
    ctx = flask_app.test_request_context()
    ctx.push()
    app.test_client_class = FlaskClient
    return app.test_client()


# def force_login(email=None):
#     def inner(f):
#         @functools.wraps(f)
#         def wrapper(*args, **kwargs):
#             if email:
#                 for key, val in kwargs.items():
#                     if isinstance(val, FlaskClient):
#                         with val:
#                             with val.session_transaction() as sess:
#                                 sess['_user_id'] = email
#                             return f(*args, **kwargs)
#             return f(*args, **kwargs)
#
#         return wrapper
#
#     return inner


@decorator
def force_login(func, email=None, *args, **kwargs):
    for arg in args:
        if isinstance(arg, FlaskClient):
            with arg:
                with arg.session_transaction() as sess:
                    sess['_user_id'] = email
            return func(*args, **kwargs)
    return func(*args, **kwargs)


def login_user(sess, email):
    sess['_user_id'] = email


@decorator
def force_login(func, cb=None, *args, **kwargs):
    for arg in args:
        if isinstance(arg, FlaskClient):
            with arg:
                with arg.session_transaction() as sess:
                    cb(sess)
            return func(*args, **kwargs)
    return func(*args, **kwargs)


def test_index_page__not_logged_in(client):
    res = client.get('/')
    assert res.status_code == 401


def test_index_page__logged_in(client):
    with client:
        client.post('/login', data=dict(email='test@gmail.com', password='test'))
        res = client.get('/')
        assert res.status_code == 200


@force_login(cb=lambda s: login_user(s, 'test@gmail.com'))
def test_index_page__logged_in2(client):
    res = client.get('/')
    assert res.status_code == 200
