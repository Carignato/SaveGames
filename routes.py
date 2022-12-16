from flask import Flask
from handler_games.games import blueprint_games
from handler_password.password import blueprint_password
from handler_register.register import blueprint_register

app = Flask(__name__)   
app.register_blueprint(blueprint_games)
app.register_blueprint(blueprint_password)
app.register_blueprint(blueprint_register)

