import os
import sys

sys.path.append(os.getcwd())

from flask import Flask
from app.routes.file_process import fileProcessRoute

def registerBP(app: Flask):
    app.register_blueprint(fileProcessRoute, url_prefix='/file')
    