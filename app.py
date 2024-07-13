from banana import Banana
from waitress import serve


app = Banana()

if __name__ == "__main__":
    app.run_server()
