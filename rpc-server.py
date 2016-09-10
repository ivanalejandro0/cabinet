#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from functools import wraps
from flask import Flask, session, request
from flask_jsonrpc import JSONRPC
from flask_jsonrpc.exceptions import InvalidCredentialsError

from cabinet import Cabinet

SECURITY_SALT = 'something to be changed in production'

app = Flask(__name__)


def authenticate(f, f_check_auth):
    @wraps(f)
    def _f(*args, **kwargs):
        token = request.headers.get('token')
        if not f_check_auth(token):
            raise InvalidCredentialsError()
        return f(*args, **kwargs)
    return _f


jsonrpc = JSONRPC(app, '/api/v1', auth_backend=authenticate)

account_id = 'my-name@my-company.com'
password = b'asdfasdf'

name = 'test-vault'
temp_config_path = os.path.join(os.getcwd(), 'test.data', 'secrets')
test_vault_path = os.path.join(os.getcwd(), 'test.data', 'vaults')
cab = Cabinet(account_id, password, temp_config_path)
cab.open(name, test_vault_path)


def check_auth(token):
    token = request.headers.get('token')
    if 'token' in session:
        return token == session['token']
    return False


@jsonrpc.method('App.get_all')
def get_all():
    return cab.get_all()


@jsonrpc.method('App.get(name=str)')
def get(name):
    return cab.get(name)


@jsonrpc.method('App.add(item=dict)')
def add(item):
    return cab.add(item)


@jsonrpc.method('Cabinet.test', authenticated=check_auth)
def index():
    return u'hello world!'


@jsonrpc.method('App.echo(name=str) -> str', authenticated=check_auth)
def echo(name='Flask JSON-RPC'):
    return u'Hello {0}'.format(name)


def get_random_open_port():
    # # serve on a random port:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


if __name__ == '__main__':
    app.secret_key = 'something really really secret =D'
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(port=5000, debug=True)  # only localhost, default port

    # port = get_random_open_port()
    # app.run(port=port)
