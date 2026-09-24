from app import Spiral4DApp
from config import Config

if __name__ == "__main__":
    app_config = Config()
    app = Spiral4DApp(app_config)
    app.run()
