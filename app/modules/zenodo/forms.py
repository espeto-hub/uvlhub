from flask_wtf import FlaskForm
from wtforms import SubmitField


class FakeForm(FlaskForm):
    submit = SubmitField('Save zenodo')
