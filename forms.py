# -*- coding: utf-8 -*-

from wtforms import Form 
from wtforms import TextAreaField, TextField, FloatField
from wtforms.validators import Length, NumberRange,required
from wtforms import PasswordField


class PredictionForm(Form):
  
  text = TextAreaField('Tweet',[Length(max=150),required()])
    

class LoginForm(Form):
    """Render HTML input for user login form.

    Authentication (i.e. password verification) happens in the view function.
    """
    username = TextField('Username', [required()])
    password = PasswordField('Password')