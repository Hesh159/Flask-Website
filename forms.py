from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import InputRequired, EqualTo, Email, Length, NumberRange
from wtforms.fields.html5 import EmailField


class RegistrationForm(FlaskForm):
    user_id = StringField('User id:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, message='Password must be minimum 8 characters long!')])
    password2 = PasswordField('Confirm password:', validators=[InputRequired(), EqualTo('password', message='Must be identical to password')])
    email = EmailField('Enter your email address:', validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    user_id = StringField('User id:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField('Submit')

class StockAmountForm(FlaskForm):
    amount = SelectField('Choose amount:', coerce=int)
    submit = SubmitField('Add to Cart')

class ReviewForm(FlaskForm):
    rating = SelectField('How happy were you with this booze?', coerce = int, choices=[(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)])
    review = StringField('Your review (max 500 chars)', validators=[InputRequired(), Length(max=500, message='Review must be no more than 500 characters long.')])
    submit = SubmitField('Submit')

class ProductEditForm(FlaskForm):
    newName = StringField('Updated product name', validators=[InputRequired()])
    newPrice = FloatField('Updated product price', validators=[InputRequired()])
    newDescription = StringField('Updated description')
    submit = SubmitField('Submit')

class StockEditForm(FlaskForm):
    stockEdit = IntegerField('Insert stock increase / decrease', validators=[InputRequired()])
    submit = SubmitField('Submit')

class NewProductForm(FlaskForm):
    name = StringField('Product name', validators=[InputRequired()])
    price = FloatField('Product price', validators=[InputRequired()])
    stock = IntegerField('Stock', validators=[InputRequired()])
    description = StringField('Description')
    submit = SubmitField('Submit')

class NewAdminForm(FlaskForm):
    admin_id = StringField('Admin id:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, message='Password must be minimum 8 characters long!')])
    password2 = PasswordField('Confirm password:', validators=[InputRequired(), EqualTo('password', message='Must be identical to password')])
    submit = SubmitField('Submit')

class changePasswordForm(FlaskForm):
    user_id = StringField('User id:', validators=[InputRequired()])
    email = EmailField('Enter the email address associated with this user id:', validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')

class TokenForm(FlaskForm):
    token = StringField('Copy the token you received in the email sent to you:', validators=[InputRequired()])
    submit = SubmitField('Submit')

class NewPasswordForm(FlaskForm):
    password = PasswordField('New Password:', validators=[InputRequired(), Length(min=8, message='Password must be minimum 8 characters long!')])
    password2 = PasswordField('Confirm password:', validators=[InputRequired(), EqualTo('password', message='Must be identical to password')])
    submit = SubmitField('Submit')

class contactForm(FlaskForm):
    suggestion = StringField('', validators=[InputRequired(), Length(max=500, message='Review must be no more than 500 characters long.')])
    submit = SubmitField('Submit')

class CheckoutForm(FlaskForm):
    address = StringField('Insert your address', validators=[InputRequired()])
    submit = SubmitField('Buy')