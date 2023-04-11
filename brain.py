from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for, request, jsonify
from db import mongo



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://duzis:duzis@financialapp.wwdb8xz.mongodb.net/?retryWrites=true&w=majority"
#

# Inicialize o PyMongo
mongo.init_app(app)

# Importe e registre os blueprints


app.register_blueprint(user_blueprint, url_prefix="/api/users")
from blueprints.users import user_blueprint
# from blueprints.families import family_blueprint
# from blueprints.financial_movements import financial_movements_blueprint
# from blueprints.goals import goals_blueprint





# app.register_blueprint(family_blueprint, url_prefix="/api/families")
# app.register_blueprint(financial_movements_blueprint, url_prefix="/api/financial_movements")
# app.register_blueprint(goals_blueprint, url_prefix="/api/goals")

# Configuração do OAuth
app.config["GOOGLE_CLIENT_ID"] = "your_google_client_id"
app.config["GOOGLE_CLIENT_SECRET"] = "your_google_client_secret"
app.config["GOOGLE_REDIRECT_URI"] = "http://localhost:5000/dashboard"

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    client_kwargs={"scope": "openid email profile"},
)

@app.route("/auth")
def auth():
    redirect_uri = url_for("auth_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/callback")
def auth_callback():
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token)
    # Salve as informações do usuário no banco de dados MongoDB
    return jsonify(user_info)

if __name__ == "__main__":
    app.run(debug=True)
