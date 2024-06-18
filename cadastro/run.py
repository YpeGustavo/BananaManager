from dash import Dash

from .layout import layout
from .configs import CONFIG


def run():
    app = Dash(assets_folder=r"cadastro\assets")
    app.layout = layout

    if "port" not in CONFIG:
        CONFIG["port"] = 8050
    if "debug" not in CONFIG:
        CONFIG["debug"] = False

    app.run(port=CONFIG["port"], debug=CONFIG["debug"])


# if __name__ == "__main__":
#     run()
