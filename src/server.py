import os
import re
from flask import Flask, redirect, url_for, render_template, request
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from threading import Thread
import requests
import json
import config.config as config
import pymongo
from cogs.server_utility import check_alt, check_alt_and_create

app = Flask(__name__,
            template_folder="views", static_folder='assets')
client = pymongo.MongoClient(config.mongodb)
database = client['main']
collection_users = database.get_collection("users")
collection_guilds = database.get_collection("guilds")


app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
# !! Only in development environment.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = config.bot_id
app.config["DISCORD_CLIENT_SECRET"] = config.bot_secret
app.config["DISCORD_BOT_TOKEN"] = config.bot_token
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:8080/auth/callback"

discord = DiscordOAuth2Session(app)


@app.route("/auth/login/")
async def login():
    return discord.create_session(scope=['connections', 'email', 'guilds', 'identify'])


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("/auth/login"))


@app.route("/auth/callback")
async def callback():
    data = discord.callback()
    redirect_to = data.get("redirect", "/verification")
    return redirect(redirect_to)


@app.errorhandler(404)
async def page_not_found(error):
    return redirect("/404")


@app.route("/logout/")
async def logout():
    discord.revoke()
    return redirect(url_for(".index"))


@app.route("/404")
async def error404():
    return render_template('404.html'), 404


@app.route("/support")
async def support():
    return redirect('https://discord.gg/GfVWxC79Km')


@app.route("/invite")
async def invite():
    return discord.create_session(scope=["bot", "applications.commands"], permissions=537258065, redirect=f"/")


@app.route("/")
async def index():
    if not discord.authorized:
        return render_template('index.html', authorized=False)
    user = discord.fetch_user()
    return render_template('index.html')


@app.route("/verification")
async def verify():
    if not discord.authorized:
        return render_template('verification.html', verified=False)
    user = discord.fetch_user()
    ip_api = requests.get(url='https://api.myip.com').json()
    user_data = collection_users.find_one({"user_id": user.id})
    if user_data:
        if user_data['verified'] == True:
            verified = True
            verified_1 = True
        else:
            if user_data:
                check_alt_1 = await check_alt(user,ip_api)
                if check_alt_1 == True:
                    verified = 'flagged'
                    verified_1 = 'Alt'
                else:
                    verified = True
                    verified = False
            else:
                check_alt_1 = await check_alt_and_create(user,ip_api)
                if check_alt_1 == True:
                    verified = 'flagged'
                    verified_1 = 'Alt'
                else:
                    verified = True
                    verified_1 = False
    else:
        check_alt_ = await check_alt_and_create(user,ip_api)
        if check_alt_ == True:
            verified = 'flagged'
            verified_1 = 'Alt'
        else:
            verified = True
            verified_1 = False
    user_data = collection_users.find_one({"user_id": user.id})
    return render_template('verification.html', verified=verified, verified_1=verified_1,user=user)


def run():
    app.run(port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
