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
