from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, TextAreaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
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
    image = FileField() #validators=[FileAllowed(image, 'Image only!'), FileRequired('File was empty!')]) #TextAreaField('Image')
    submit = SubmitField('Add')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators = [
        DataRequired(),
        Length(min=4, max=6)
        # validators.EqualTo('confirm_new_password', message='Passwords must match')
    ])
    confirm_new_password = PasswordField(
        label=('Confirm Password'),
        validators=[DataRequired(message='*Required'),
        EqualTo('new_password', message='Both password fields must be equal!')])
    submit = SubmitField("Change Password")
