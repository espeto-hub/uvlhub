import wtforms
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, NoneOf

from app import apprise
from app.modules.bot.services import BotService


class BotForm(FlaskForm):
    id = wtforms.HiddenField()
    name = wtforms.StringField('Name', validators=[DataRequired('Please input a name.'), Length(min=3, max=50)])
    service_name = wtforms.SelectField('Service', choices=['Select one...'] + apprise.service_names,
                                       validators=[DataRequired('Please select a service'),
                                                   NoneOf(['Select one...'], 'Please select a service')])
    service_url = wtforms.URLField('URL', validators=[DataRequired('Please input an URL.')])
    enabled = wtforms.BooleanField('Enabled', default=True)
    on_download_dataset = wtforms.BooleanField('When someone downloads one of my datasets', default=False)
    on_download_file = wtforms.BooleanField('When someone downloads one of my files', default=False)
    user_id = wtforms.HiddenField()
    test = wtforms.SubmitField('Test')
    is_tested = wtforms.HiddenField(default='false')
    submit = wtforms.SubmitField('Save')

    def validate_service_url(self, field):
        is_valid, error = apprise.is_url_valid(field.data, self.service_name.data)
        if not is_valid:
            raise wtforms.ValidationError(str(error))

    def validate_name(self, field):
        service = BotService()
        bot = service.get_by_user_and_name(user_id=self.user_id.data, name=field.data)
        if bot:
            raise wtforms.ValidationError('Bot with this name already exists')
