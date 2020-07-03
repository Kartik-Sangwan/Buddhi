from main.forms import (RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from main.models import User, Post
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt, session, mail
from flask_login import login_user, current_user, logout_user, login_required
from main.plaid_server import *
from werkzeug.utils import secure_filename
from flask_mail import Message
import json
import requests
import secrets
import os

from flask_mail import Mail, Message

# I have given access to less secure apps for loggin into gmail account for this checking email. Need to fix later
# Sending an email
# app.config['MAIL_SERVER']='smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'imployie@gmail.com'
# app.config['MAIL_PASSWORD'] = 'Wewillrockyou'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

# mail = Mail(app)
# Creating server side session instead of cookie


@app.route("/")
# @app.route("/home")
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
                    # redirect(next_page) if next_page else redirect(url_for("employee"))
                    plaid_authenticate()
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
    user = User.query.filter_by(username=session["username"]).first()
    print(user)
    registered = False
    if user and user.access_token != None:
        registered = True
        print(user.access_token)
    print(user.image)
    image_file = url_for("static", filename="profile_pics/" + current_user.image)
    return render_template(
        "employerHome.html", title="Employer Page", username=session["username"], image_file=image_file,
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
# <<<<<<< HEAD
    if(user_access_token == None):
        return render_template("singleEmployee.html", error="Employee has not authenticated yet.")
    response = get_auth(user_access_token)
    liabilities_info = get_liabilities(user_access_token)
    if (not(liabilities_info["error"] is None) or not(response["error"] is None)):
        return "Error is raised"
    # print(liabilities_info["info"])
    
    # 
    # Can a person have multiple student loans?? as "student returns a list"
    # 
    # 
    liabilities_inner_info = liabilities_info["info"]["student"][0]
    liabilities_dict = {"payoff-date": liabilities_inner_info["expected_payoff_date"], "interest-rate": liabilities_inner_info["interest_rate_percentage"], 
    "next-due-date": liabilities_inner_info["next_payment_due_date"], "payments-remaining": liabilities_inner_info["pslf_status"]["payments_remaining"]}
    res = response['auth']['accounts'][7]
    student_loan = res["balances"]["current"]
    currency = res["balances"]['iso_currency_code']
    return render_template("singleEmployee.html", user=user, student_loan=student_loan, currency=currency, error='', loan_info=liabilities_dict)
# =======
    # if user_access_token == None:
    #     return render_template(
    #         "singleEmployee.html", error="Employee has not authenticated yet."
    #     )
    # res = get_auth(user_access_token)["auth"]["accounts"][7]
    # # employee_dict = json.loads(res)
    # # print(res)
    # student_loan = res["balances"]["current"]
    # currency = res["balances"]["iso_currency_code"]
    # return render_template(
    #     "singleEmployee.html",
    #     user=user,
    #     student_loan=student_loan,
    #     currency=currency,
    #     error="",
    # )

# >>>>>>> employer-section

@app.route("/employer/add")
def add_employee():
    return render_template("employerAdd.html")


@app.route("/employee", methods=["GET", "POST"])
@login_required
def employee():
    user = User.query.filter_by(username=session["username"]).first()
    print(user)
    registered = False
    if user and user.access_token != None:
        registered = True
        print(user.access_token)
    print(user.image)
    image_file = url_for("static", filename="profile_pics/" + current_user.image)
    return render_template(
        "employeeHome.html",
        username=session["username"],
        registered=registered,
        image_file=image_file
    )


# Save picture in a local directory for now later database maybe
def save_picture(form_picture):
    random_name = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_f_name = random_name + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics/", picture_f_name)
    
    form_picture.save(picture_path)
    return picture_f_name


# Update username and the password of the current logged in user.
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/employee/updateUsrPass", methods=["GET", "POST"])
@login_required
def updateUsrPass():

    form = UpdateAccountForm()
    if request.method == 'POST':
            flag = 0
            if 'file' not in request.files:
                print('No file part')
                flash('No file part')
                flag = 1
                
            if flag == 0:
                file = request.files['file']

                if file.filename == '':
                    print('no file selected')
                    flash('No selected file')
                    
                
                if allowed_file(file.filename):
                    file = secure_filename(file.filename)
                    pic_f_name = save_picture(request.files['file'])
                    current_user.image = pic_f_name
                    db.session.commit()
               

    if form.validate_on_submit():
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


@app.route("/show_all")
def show():
    users = User.query.all()
    for user in users:
        print(user.username, user.access_token)

    return "check server console"

# <<<<<<< HEAD
@app.route("/mail")
def send_mail():
    msg = Message(subject='Verification of account needed', sender = 'imployie@gmail.com', recipients = ['adityagoyaldoon@gmail.com'])
    # msg.body = "This is a checking email from Imployie"
    msg.html = render_template("mailTemplate.html")

    mail.send(msg)
    flash(f'Request sent successfully', 'success')

    return redirect(url_for('employer_employees'))
# =======
# Send this user an email for reset password.
def send_reset_email(user):
    token = user.get_reset_token()
    print(user.email)
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''
    To reset Your Password visit the following link.
{url_for('reset_token', token = token, _external=True)}
Thanks and enjoy using the platform and give us feedback.
    '''
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        # Send this user an email for reset password.
        send_reset_email(user)
        flash('An email has been sent to reset your password.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = "Reset Password", form = form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid/expired token', 'warning')
        return redirect(url_for('reset_request'))
    
    # Valid token thus change this user can update his password.
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! Please login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title = "Reset Password", form = form)
# >>>>>>> employer-section
