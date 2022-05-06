import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

api = Blueprint('api', __name__, template_folder='templates', url_prefix="/api")

@api.route('/')
def show():
    return "Should not be accessed!"
