from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired, Length, URL

from app import apprise


class CreateBotForm(FlaskForm):
    name = wtforms.StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    service_url = wtforms.URLField('Service URL', validators=[DataRequired()])
    enabled = wtforms.BooleanField('Enabled', default=True)
    on_download_dataset = wtforms.BooleanField('On download dataset', default=False)
    submit = wtforms.SubmitField('Save')
