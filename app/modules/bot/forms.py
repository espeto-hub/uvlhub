import wtforms
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length

from app import apprise
from app.modules.bot.services import BotService


class BotForm(FlaskForm):
    id = wtforms.HiddenField()
    name = wtforms.StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    service_name = wtforms.SelectField('Service', choices=['Select one...'] + apprise.service_names)
    service_url = wtforms.URLField('URL', validators=[DataRequired()])
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
        if not self.id:
            service = BotService()
            bot = service.get_by_user_and_name(user_id=self.user_id.data, name=field.data)
            if bot:
                raise wtforms.ValidationError('Bot with this name already exists')
