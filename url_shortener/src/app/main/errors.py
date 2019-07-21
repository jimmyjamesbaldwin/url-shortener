from flask import render_template
from app.main.views import main

@main.app_errorhandler(500)
def internal_server_error(_):
    return render_template('errors/500.html'), 500
