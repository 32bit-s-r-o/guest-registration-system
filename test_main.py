from flask import Flask, Blueprint
from config import Config

# Create a minimal Flask app
app = Flask(__name__)

# Create a minimal main blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Hello World"

# Register the blueprint
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True) 