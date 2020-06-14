from main.forms import RegistrationForm, LoginForm
from main.models import User, Post
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt, session
from flask_login import login_user, current_user, logout_user, login_required
from main.plaid_server import *
import json
import requests

# Creating server side session instead of cookie

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Already registered', 'success')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password, category=form.category.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created you can now login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Login', form=form)

# TODO: authorize if user is employer or employee. Can a user be both?

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        flash('Already Logged In.', 'success')
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            flash(f'Login Successful. Welcome {user.username}', 'success')

            # Stored until user has logged out
            session['username'] = user.username
            session['email'] = user.email

            if form.category.data == 'Employer':
                return redirect(next_page) if next_page else redirect(url_for('employer'))
            elif form.category.data == 'Employee':
                return redirect(next_page) if next_page else redirect(url_for('employee'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Check your email and password and try again!', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/employer")
def employer():
    return render_template("employerHome.html", title="Employer Page", username=session['username'])


@app.route("/employer/company")
def company():
    return render_template("companyInfo.html")


@app.route("/employer/employees")
def employer_employees():

    # TODO: check who is whose employee. Right now, showing all employees in the database
    users = User.query.filter_by(category='Employee').all()
    return render_template('employeesList.html', users=users)


@app.route("/employer/employees/<int:id>")
def single_employee(id):
    user = User.query.get(id)
    user_access_token = user.access_token
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
    liabilities_dict = {"payoff-data": liabilities_inner_info["expected_payoff_date"], "interest-rate": liabilities_inner_info["interest_rate_percentage"], 
    "next-due-date": liabilities_inner_info["next_payment_due_date"], "payments-remaining": liabilities_inner_info["pslf_status"]["payments_remaining"]}
    res = response['auth']['accounts'][7]
    student_loan = res["balances"]["current"]
    currency = res["balances"]['iso_currency_code']
    return render_template("singleEmployee.html", user=user, student_loan=student_loan, currency=currency, error='', loan_info=liabilities_dict)

@app.route("/employer/add")
def add_employee():
    return render_template('employerAdd.html')


@app.route("/employee")
def employee():
    user = User.query.filter_by(username=session['username']).first()
    registered=False
    if user.access_token != None:
        registered=True
    return render_template("employeeHome.html", username = session['username'], registered=registered)


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged Out Successfully.', 'success')
    session.pop("username", None)
    session.pop("email", None)
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/show_all")
def show():
    users = User.query.all()
    for user in users:
        print(user.username, user.access_token)

    return "check server console"
