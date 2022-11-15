from app_help2 import main
import threading
import os
from flask import Flask
app = Flask(__name__)


class FlaskThread(threading.Thread):
    def run(self) -> None:
        app.run(threaded=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


class TelegramThread(threading.Thread):
    def run(self) -> None:
        main()


if __name__ == "__main__":
    flask_thread = FlaskThread()
    flask_thread.start()

    main()
