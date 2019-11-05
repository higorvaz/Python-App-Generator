from flask import Flask
from app.user import user_routes
app = Flask(__name__)

# temporary secret key
app.secret_key = "ABC"

app.register_blueprint(user_routes.user_bp)
