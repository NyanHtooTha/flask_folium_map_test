from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form, FormField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea



class TestForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    latlng = StringField('Clicked location:', default="")
    locate = StringField('Current location:', default="")
    submit = SubmitField('Submit')


class Info(Form):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone Number')
    location = StringField('Location')
    address = StringField('Address', widget=TextArea())


class ExpressForm(FlaskForm):
    sender_info = FormField(Info)
    receiver_info = FormField(Info)
    submit = SubmitField('Submit')
