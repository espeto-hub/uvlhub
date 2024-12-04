from app.modules.bot.repositories import BotRepository
from core.services.BaseService import BaseService


class BotService(BaseService):
    def __init__(self):
        super().__init__(BotRepository())
