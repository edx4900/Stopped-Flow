from dash import Dash
from layout import create_layout
from callbacks import register_callbacks

def create_dash_app(key):
    app = Dash(__name__)
    app.layout = create_layout(key) 
    return app

def run_dash(key):
    app = create_dash_app(key)
    register_callbacks(app, key)
    app.run_server(debug=True)
    # app.run(jupyter_mode="external")
