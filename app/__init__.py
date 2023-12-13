from flask import Flask, render_template
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'

    from app.routes import registerBP
    
    registerBP(app)
    
    @app.route('/')
    def index():
        return render_template('upload_form.html')

    @app.route("/test/")
    def test_page():
        return "<h1> why pay $20 for onlyfans when the hub is free </h1>"
    return app