from main.forms import RegistrationForm, LoginForm, UpdateAccountForm
from main.models import User, Post
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt, session
from flask_login import login_user, current_user, logout_user, login_required
from main.plaid_server import *
import json
import requests
import secrets
import os


# Creating server side session instead of cookie


@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("Already registered", "success")
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            category=form.category.data,
        )
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created you can now login!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Login", form=form)


# TODO: authorize if user is employer or employee. Can a user be both?


@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        flash("Already Logged In.", "success")
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash(f"Login Successful. Welcome {user.username}", "success")

            # Stored until user has logged out
            session["username"] = user.username
            session["email"] = user.email

            if form.category.data == "Employer":
                return (
                    redirect(next_page) if next_page else redirect(url_for("employer"))
                )
            elif form.category.data == "Employee":
                return (
                    redirect(next_page) if next_page else redirect(url_for("employee"))
                )
            else:
                return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash(
                "Login Unsuccessful. Check your email and password and try again!",
                "danger",
            )

    return render_template("login.html", title="Login", form=form)


@app.route("/employer")
def employer():
    return render_template(
        "employerHome.html", title="Employer Page", username=session["username"]
    )


@app.route("/employer/company")
def company():
    return render_template("companyInfo.html")


@app.route("/employer/employees")
def employer_employees():

    # TODO: check who is whose employee. Right now, showing all employees in the database
    users = User.query.filter_by(category="Employee").all()
    return render_template("employeesList.html", users=users)


@app.route("/employer/employees/<int:id>")
def single_employee(id):
    user = User.query.get(id)
    user_access_token = user.access_token
    if user_access_token == None:
        return render_template(
            "singleEmployee.html", error="Employee has not authenticated yet."
        )
    res = get_auth(user_access_token)["auth"]["accounts"][7]
    # employee_dict = json.loads(res)
    # print(res)
    student_loan = res["balances"]["current"]
    currency = res["balances"]["iso_currency_code"]
    return render_template(
        "singleEmployee.html",
        user=user,
        student_loan=student_loan,
        currency=currency,
        error="",
    )


@app.route("/employer/add")
def add_employee():
    return render_template("employerAdd.html")


@app.route("/employee", methods=["GET", "POST"])
@login_required
def employee():
    user = User.query.filter_by(username=session["username"]).first()
    registered = False
    if user and user.access_token != None:
        registered = True
    image_file = url_for("static", filename="profile_pics/" + current_user.image)
    return render_template(
        "employeeHome.html",
        username=session["username"],
        registered=registered,
        image_file=image_file,
    )


# Save picture in a local directory for now later database maybe
def save_picture(form_picture):
    random_name = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_f_name = random_name + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics/", picture_f_name)
    app.logger.info("HELLO")
    form_picture.save(picture_path)
    return picture_f_name


# Update username and the password of the current logged in user.


@app.route("/employee/updateUsrPass", methods=["GET", "POST"])
@login_required
def updateUsrPass():

    form = UpdateAccountForm()
    print("HERE")
    if form.validate_on_submit():
        print(form.picture.data)
        if form.picture.data:
            print("HERE2")
            picture_file_name = save_picture(form.picture.data)
            current_user.image = picture_file_name
        # Update the credential of this user.
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        image_file = url_for("static", filename="profile_pics/" + current_user.image)
        return render_template(
            "employeeHome.html",
            username=current_user.username,
            registered=True,
            image_file=image_file,
        )

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for("static", filename="profile_pics/" + current_user.image)
    return render_template("editProfile.html", form=form, image_file=image_file)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged Out Successfully.", "success")
    session.pop("username", None)
    session.pop("email", None)
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    return render_template(
        "employeeHome.html",
        username=current_user.username,
        registered=True,
        image_file=image_file,
    )


@app.route("/show_all")
def show():
    users = User.query.all()
    for user in users:
        print(user.username, user.access_token)

    return "check server console"
