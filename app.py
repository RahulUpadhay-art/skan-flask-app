# app.py - MINIMAL FLASK APP
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'skan-demo-2024'
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
