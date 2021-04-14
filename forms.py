from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, TextAreaField, IntegerField, DateTimeField
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
    discount = FloatField('Discount')
    description = TextAreaField('Description')
    image = FileField() #validators=[FileAllowed(image, 'Image only!'), FileRequired('File was empty!')]) #TextAreaField('Image')
    submit = SubmitField('Add')

class AddProductFromAdminForm(FlaskForm):
    product_name = StringField('Product', [DataRequired()])
    barcode = StringField('Barcode')
    brand = StringField('Brand')
    size = StringField('Size')
    price = FloatField('Price')
    discount = FloatField('Discount')
    description = TextAreaField('Description')
    image = FileField() #validators=[FileAllowed(image, 'Image only!'), FileRequired('File was empty!')]) #TextAreaField('Image')
    #submit = SubmitField('Add')


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


class ChangePersonalInfo(FlaskForm):
    firstName = StringField('First Name',validators=[DataRequired()])
    middleName = StringField('Middle Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    emailId = StringField('Email Id', validators=[DataRequired()])
    phoneNo = StringField('Phone No', validators=[DataRequired()])
    submit = SubmitField("Save Changes")
    cancel = SubmitField('Cancel')


class ChangeAddress(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    addressLine= StringField('Address Line', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    postalCode = StringField('Postal Code', validators=[DataRequired()])
    country= StringField('country', validators=[DataRequired()])
    submit = SubmitField("Save Changes")
    cancel = SubmitField("Cancel")


class OrderForm(FlaskForm):
    card_number = StringField('Card Number', [DataRequired()])
    card_holder = StringField('Card Holder', [DataRequired()])
    expires = DateTimeField('Expires', [DataRequired()])
    cvc = StringField('CVC', [DataRequired()])
    name = StringField('Full Name', [DataRequired()])
    address = TextAreaField('Address', [DataRequired()])
    city = StringField('City', [DataRequired()])
    post_code = StringField('Post code', [DataRequired()])
    phone_number = StringField('Phone Number', [DataRequired()])
    recipient_email = StringField('Recipient Email', [DataRequired()])
    submit = SubmitField('Order')


class UsersForm(FlaskForm):
    username = StringField('User Name', [DataRequired()])
    email = StringField('Email', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    active = BooleanField('Is Active?')
    isAdmin = BooleanField('Is Admin?')
    #accept_terms = BooleanField('I accept the Terms of Service and Privacy Notice', [DataRequired()])

