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

    def create_bot(self, form):
        created_instance = self.create(
            name=form.name.data,
            service_name=form.service_name.data,
            service_url=form.service_url.data,
            enabled=form.enabled.data,
            on_download_dataset=form.on_download_dataset.data,
            user_id=form.user_id.data,
        )
        return created_instance, None

    def get_by_user_and_name(self, user_id, name):
        return self.repository.get_by_user_and_name(user_id, name)


class BotMessagingService(BaseService):
    def __init__(self):
        super().__init__(BotRepository())

    @staticmethod
    def send_test_message(urls: str | list[str]):
        return apprise.send_test_message(urls)
