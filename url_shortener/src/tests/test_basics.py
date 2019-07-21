import unittest
import random
from app import create_app, db
from flask import current_app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app('testing')
        self.app = app.test_client()

    def test_route_hello_world(self):
        res = self.app.get("/")
        assert res.status_code == 200
        assert b"URL shortener" in res.data