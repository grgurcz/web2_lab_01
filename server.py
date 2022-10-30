import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from datetime import datetime

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request

from load_data import load_initial_data

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


INITIAL_DATA = load_initial_data()
ADMIN_USERS = ['grgur.crnogorac6']


@app.route("/")
def schedule():
    INITIAL_DATA.get_points_table()
    return render_template(
        "schedule.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        data=INITIAL_DATA,
        admins=ADMIN_USERS
    )


@app.route('/standings')
def standings():
    return render_template(
        "standings.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        data=INITIAL_DATA,
        admins=ADMIN_USERS
    )


@app.route("/round/<int:round_num>")
def round(round_num):
    games = INITIAL_DATA.get_round_games(round_num)
    comments = INITIAL_DATA.get_round_comments(round_num)
    
    return render_template(
        "round.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        round_num = round_num,
        data=INITIAL_DATA,
        games=games,
        comments=comments,
        admins=ADMIN_USERS
    )

@app.route("/match")
@app.route("/match/<int:match_id>")
def match(match_id=-1):
    if match_id == -1:
        return render_template(
            "newmatch.html",
            session=session.get("user"),
            pretty=json.dumps(session.get("user"), indent=4),
            data=INITIAL_DATA,
            admins=ADMIN_USERS
        )

    return render_template(
        "editmatch.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        data=INITIAL_DATA,
        match_data=INITIAL_DATA.all_games[match_id],
        admins=ADMIN_USERS
    )


@app.route('/editmatch', methods = ['POST'])
def editmatch():
    match_id = int(request.form['match_id'])
    team_1_score = int(request.form['team_1_score'])
    team_2_score = int(request.form['team_2_score'])
    round_num = int(request.form['round_num'])

    INITIAL_DATA.edit_game(match_id, team_1_score, team_2_score)

    return redirect(f'/round/{round_num}')


@app.route('/newmatch', methods = ['POST'])
def newmatch():
    print(request.form)
    round_num = int(request.form['round_num'])
    team_1 = request.form['team_1']
    team_2 = request.form['team_2']
    team_1_score = int(request.form['team_1_score'])
    team_2_score = int(request.form['team_2_score'])
    #match_time = datetime(request.form['match_time'])
    match_time = datetime.strptime(request.form['match_time'], "%Y-%m-%dT%H:%M")
    print('HERE')
    print(type(match_time))
    INITIAL_DATA.add_game(round_num, team_1, team_2, team_1_score, team_2_score, match_time)
    return redirect(f'/round/{round_num}')


@app.route("/comment", methods = ['POST'])
def comment():
    comment_id = int(request.form['comment_id'])
    round_num = int(request.form['round_num'])

    if 'delete' in request.form:
        INITIAL_DATA.remove_comment(comment_id)

        return redirect(f'/round/{round_num}')
    
    new_text = request.form['new_text']
    INITIAL_DATA.edit_comment(comment_id, new_text)

    return redirect(f'/round/{round_num}')


@app.route('/new/comment', methods = ['POST'])
def add_comment():
    round_num = int(request.form['round_num'])
    new_text = request.form['new_text']
    username = request.form['username']
    
    INITIAL_DATA.add_comment(round_num, new_text, username)

    return redirect(f'/round/{round_num}')


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("schedule", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))