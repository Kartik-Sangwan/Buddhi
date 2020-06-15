from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User


class RegistrationForm(FlaskForm):
    category = RadioField(
        "Category", choices=[("Employer", "Employer"), ("Employee", "Employee")]
    )

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired()])

    confirm_pass = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )

    submit = SubmitField("Sign Up")

    remember = BooleanField("Remember Me")

    def validate_username(self, username):

        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError("Username already taken. Please choose another one.")

    def validate_email(self, email):

        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError("Email already taken. Please choose another one.")


class LoginForm(FlaskForm):

    category = RadioField(
        "Category", choices=[("Employer", "Employer"), ("Employee", "Employee")]
    )

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")

    submit = SubmitField("Sign In")


class UpdateAccountForm(FlaskForm):

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )

    email = StringField("Email", validators=[DataRequired(), Email()])

    picture = FileField(
        "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()

            if user:
                raise ValidationError(
                    "Username already taken. Please choose another one."
                )

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError("Email already taken. Please choose another one.")

