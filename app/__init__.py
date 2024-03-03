
from flask import Flask

app = Flask(__name__,template_folder='../templates',static_folder='../static')


from app import authentication
from app import profile
from app import personnel
from app import guide