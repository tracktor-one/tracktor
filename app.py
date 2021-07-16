import os

from app import app

if __name__ == '__main__':
    app.run(debug=(os.getenv("DEBUG", default=0) == "1"))
