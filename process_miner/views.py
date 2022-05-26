import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

views = Blueprint('views', __name__, template_folder='templates')


@views.route('/')
def show():
    return render_template('index.html')
