from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SignInForm(FlaskForm):
    firstName = StringField("First Name", validators=[DataRequired()])
    lastName = StringField("Last Name", validators=[DataRequired()])
    email = StringField(
        "Email",
        validators=[
            Length(min=7),
            Email(message="Please enter a valid email."),
            DataRequired(),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            Length(min=8, message="Please select a stronger password"),
            DataRequired(),
        ],
    )
    passwordConfirm = PasswordField(
        " Re-Enter Your Password",
        validators=[
            EqualTo("password", message="Passwords don't match"),
            DataRequired(),
        ],
    )
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):

    email = StringField(
        "Email", validators=[DataRequired(), Email(message="Enter a valid email.")]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")