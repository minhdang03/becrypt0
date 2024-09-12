from flask import Flask
from flask_cors import CORS
from routes.crypto import crypto_bp
from routes.api import api_bp

app = Flask(__name__)
CORS(app)

# Đăng ký blueprint
app.register_blueprint(crypto_bp, url_prefix='/crypto')
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)