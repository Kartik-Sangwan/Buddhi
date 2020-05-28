import os

from flask import Flask, render_template, request, session

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():

    return render_template("login.html")


@app.route("/loggedin")
def loggedin():

    # return render_template("index.html")
    return "You have logged in "