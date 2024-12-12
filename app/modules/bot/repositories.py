from app.modules.bot.models import Bot
from core.repositories.BaseRepository import BaseRepository


class BotRepository(BaseRepository):
    def __init__(self):
        super().__init__(Bot)

    def get_all_by_user(self, user_id):
        return self.model.query.filter_by(user_id=user_id).all()

    def get_by_user_and_name(self, user_id, name):
        return self.model.query.filter_by(user_id=user_id, name=name).first()

    def delete(self, bot):
        return bot.delete()
