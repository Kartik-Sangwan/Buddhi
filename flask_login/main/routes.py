from main.forms import RegistrationForm, LoginForm
from main.models import User, Post
from flask import render_template, url_for, flash, redirect, request, session
from main import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

# Creating server side session instead of cookie

@app.route('/')
@app.route('/home')
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


@app.route("/employee/employees")
def employer_employees():
    return render_template('employeesList.html')


@app.route("/employer/add")
def add_employee():
    return render_template('employerAdd.html')


@app.route("/employee")
def employee():
    return "Welcome employee"


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

