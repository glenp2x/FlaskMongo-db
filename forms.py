from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import validators


class CustomerSignupForm(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    confirm_password = PasswordField('Confirm Password')
    accept_terms = BooleanField('I accept the Terms of Service and Privacy Notice', [DataRequired()])
    submit = SubmitField('Sign Up')


class CustomerLoginForm(FlaskForm):
    email = StringField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')


class AddProductForm(FlaskForm):
    product_name = StringField('Product', [DataRequired()])
    barcode = StringField('Barcode')
    brand = StringField('Brand')
    size = StringField('Size')
    price = FloatField('Price')
    description = TextAreaField('Description')
    image = TextAreaField('Image')
    submit = SubmitField('Add')
