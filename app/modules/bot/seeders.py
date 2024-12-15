from app.modules.auth.models import User
from app.modules.bot.models import Bot
from core.seeders.BaseSeeder import BaseSeeder


class BotSeeder(BaseSeeder):

    def run(self):
        user1 = User.query.filter_by(email='user1@example.com').first()

        data = [
            Bot(name='Bot 1', service_name='Discord', service_url='test://test/test', user_id=user1.id),
        ]

        self.seed(data)
