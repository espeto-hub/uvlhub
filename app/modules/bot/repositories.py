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

    def update(self, id, **kwargs):
        bot = self.get_by_id(id)
        bot.update(**kwargs)
        return bot

    def get_on_download_dataset_bots(self, user_id):
        return self.model.query.filter_by(user_id=user_id, on_download_dataset=True, enabled=True).all()
