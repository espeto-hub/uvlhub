from flask_wtf import FlaskForm
from wtforms import SubmitField


class BotForm(FlaskForm):
    submit = SubmitField('Save bot')
