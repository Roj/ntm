import json
import os

from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    send_from_directory,
)
import flask_login
from oauthlib.oauth2 import WebApplicationClient
import requests

from ntm.schema import Base, User, Game, Question
from ntm.engine import engine
from ntm import logic
from ntm import config
from ntm.create_data import legit_etl
from sqlalchemy.orm import Session


# Create tables
Base.metadata.create_all(engine)

# Fill data
with Session(engine) as session:
    legit_etl(session)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
client = WebApplicationClient(config.GOOGLE_CLIENT_ID)


@app.route("/static/<path:path>")
@flask_login.login_required
def send_report(path):
    return send_from_directory("static", path)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    with Session(engine) as session:
        user = session.query(User).filter(User.email == user_id).one_or_none()
    return user


@app.route("/")
def index():
    if flask_login.current_user.is_authenticated:
        return render_template(
            "index.html",
            user_email=flask_login.current_user.email,
        )
    else:
        return render_template("login.html", folder="templates")


def get_google_provider_cfg():
    return requests.get(config.GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )

    return redirect(request_uri)


# Login Callback
@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    result = "<p>code: " + code + "</p>"

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    result = result + "<p>token_response: " + token_response.text + "</p>"

    # return result

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
        if "@muttdata.ai" not in users_email:
            return "Please use your @muttdata.ai mail to enter!", 400
    else:
        return "User email not available or not verified by Google.", 400

    with Session(engine) as session:
        user = User(email=users_email, name=users_name)
        session.merge(user)
        session.commit()
    # Begin user session by logging the user in
    flask_login.login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


# Logout
@app.route("/logout")
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for("index"))


@app.route("/game/new")
@flask_login.login_required
def create_new_game():
    # Create new game using given email
    with Session(engine) as session:
        questions = logic.create_assortment_of_questions(session)
        game = logic.make_new_game(flask_login.current_user.email, session)
        # Commit to session
        # Return random assortment of questions and options (shuffled)
        return {
            "game_id": game.id,
            "questions": questions,
            "game_length": config.GAME_LENGTH,
            "user_name": flask_login.current_user.name,
        }


@app.route("/game/answer", methods=["POST"])
@flask_login.login_required
def check_question_anwer():
    data = request.json
    with Session(engine) as session:
        # check if game is not finished
        db_game = (
            session.query(Game).filter(Game.id == data.get("game_id")).one_or_none()
        )
        if db_game.answers >= config.GAME_LENGTH:
            return "Game is already finished"

        db_game.answers += 1
        # check question answer
        db_question = (
            session.query(Question)
            .filter(Question.filename == data.get("question_filename"))
            .one_or_none()
        )
        if db_question.correct_option != data.get("answer"):
            session.merge(db_game)
            session.commit()
            return "Incorrect"
        else:
            db_game.score += 1
            session.merge(db_game)
            session.commit()
            return "Correct"


if __name__ == "__main__":
    app.run(port=config.SERVER_PORT, debug=False, host="0.0.0.0")
