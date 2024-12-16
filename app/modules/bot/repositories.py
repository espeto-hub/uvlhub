from app.modules.bot.models import Bot
from core.repositories.BaseRepository import BaseRepository


class BotRepository(BaseRepository):
    def __init__(self):
        super().__init__(Bot)

    def get_all_by_user(self, user_id):
        return self.model.query.filter_by(user_id=user_id).all()

    def delete(self, bot):
        return bot.delete()

    def update(self, id, **kwargs):
        bot = self.get_by_id(id)
        bot.update(**kwargs)
        return bot

    def get_on_download_dataset_bots(self, user_id):
        return self.model.query.filter_by(user_id=user_id, on_download_dataset=True, enabled=True).all()

    def get_on_download_file_bots(self, user_id):
        return self.model.query.filter_by(user_id=user_id, on_download_file=True, enabled=True).all()

    def is_bot_name_unique(self, data, bot_id=None):
        return not self.model.query.filter_by(name=data).filter(Bot.id != bot_id).first()
