from app import apprise
from app.modules.bot.repositories import BotRepository
from core.services.BaseService import BaseService


class BotService(BaseService):
    def __init__(self):
        super().__init__(BotRepository())

    def get_all_by_user(self, user_id):
        return self.repository.get_all_by_user(user_id)

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    def delete(self, bot):
        return self.repository.delete(bot)

    def create_bot(self, user_id, form):
        if form.validate():
            created_instance = self.create(
                name=form.name.data,
                service_name=form.service_name.data,
                service_url=form.service_url.data,
                enabled=form.enabled.data,
                on_download_dataset=form.on_download_dataset.data,
                user_id=user_id,
            )
            return created_instance, None

        return None, form.errors
