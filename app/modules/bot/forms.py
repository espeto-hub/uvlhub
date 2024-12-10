import wtforms
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length

from app import apprise


class CreateBotForm(FlaskForm):
    name = wtforms.StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    service_name = wtforms.SelectField('Service', choices=apprise.service_names)
    service_url = wtforms.URLField('URL', validators=[DataRequired()])
    enabled = wtforms.BooleanField('Enabled', default=True)
    on_download_dataset = wtforms.BooleanField('On download dataset', default=False)
    submit = wtforms.SubmitField('Save')

    def validate_service_url(self, field):
        is_valid, error = apprise.is_url_valid(field.data, self.service_name.data)
        if not is_valid:
            raise wtforms.ValidationError(str(error))
