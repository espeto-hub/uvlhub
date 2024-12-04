from app.modules.bot.models import Bot
from core.repositories.BaseRepository import BaseRepository


class BotRepository(BaseRepository):
    def __init__(self):
        super().__init__(Bot)
