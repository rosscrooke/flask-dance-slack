import os
import time
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, redirect, url_for
from flask_dance.contrib.slack import make_slack_blueprint, slack
from flask_sslify import SSLify
from raven.contrib.flask import Sentry
CHANNEL_NAME = "general"

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
sentry = Sentry(app)
sslify = SSLify(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
app.config["SLACK_OAUTH_CLIENT_ID"] = os.environ.get("SLACK_OAUTH_CLIENT_ID")
app.config["SLACK_OAUTH_CLIENT_SECRET"] = os.environ.get("SLACK_OAUTH_CLIENT_SECRET")
slack_bp = make_slack_blueprint(scope=["identify", "chat:write:bot"])
app.register_blueprint(slack_bp, url_prefix="/login")

@app.route("/")
def index():
    if not slack.authorized:
        return redirect(url_for("slack.login"))
    resp = slack.post("chat.postMessage", data={
        "channel": "#general",
        "text": "ping",
        "icon_emoji": ":robot_face:",
    })
    assert resp.ok, resp.text
    return resp.text

    resp2 = slack.post("chat.postMessage", data={
        "channel": "#general",
        "text": "ping",
        "icon_emoji": ":robot_face:",
        "attachments": [
        {
            "text": "Choose a game to play",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "chess",
                    "text": "Chess",
                    "type": "button",
                    "value": "chess"
                },
                {
                    "name": "maze",
                    "text": "Falken's Maze",
                    "type": "button",
                    "value": "maze"
                },
                {
                    "name": "war",
                    "text": "Thermonuclear War",
                    "style": "danger",
                    "type": "button",
                    "value": "war",
                    "confirm": {
                        "title": "Are you sure?",
                        "text": "Wouldn't you prefer a good game of chess?",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                }
            ]
        }
    ]
    })
    assert resp2.ok, resp2.text
    return resp2.text


if __name__ == "__main__":
    app.run()
