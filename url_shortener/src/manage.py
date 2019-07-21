#!/usr/bin/env python
import os
from flask_script import Manager

from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'development') # development
manager = Manager(app)


@manager.command
def runserver():
    app.run(host='0.0.0.0')


@manager.command
def unittest():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
