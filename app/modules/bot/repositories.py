from app.modules.bot.models import Bot
from core.repositories.BaseRepository import BaseRepository


class BotRepository(BaseRepository):
    def __init__(self):
        super().__init__(Bot)

    def get_all_by_user(self, user_id):
        return Bot.query.filter_by(user_id=user_id).all()

    def get_by_id(self, id):
        return Bot.query.filter_by(id=id).first()

    def delete(self, bot):
        return bot.delete()
