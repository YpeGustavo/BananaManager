from dash import Dash

from .layout import layout
from .configs import CONFIG


def run():
    app = Dash(assets_folder=r"banana\assets")
    app.layout = layout
    app.run(port=CONFIG.port, debug=CONFIG.debug)
