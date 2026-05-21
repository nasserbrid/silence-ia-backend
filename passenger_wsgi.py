import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)
os.chdir(app_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(app_dir, '.env'))

from a2wsgi import ASGIMiddleware
from app.main import app

application = ASGIMiddleware(app)
