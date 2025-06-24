from flask import Flask, render_template_string
from config import Config

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Welcome to Test Page</h1>
        <p>This is a minimal test to see if Flask is working.</p>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 