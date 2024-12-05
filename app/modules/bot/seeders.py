from app.modules.auth.models import User
from core.seeders.BaseSeeder import BaseSeeder
from app.modules.bot.models import Bot


class BotSeeder(BaseSeeder):

    def run(self):
        user1 = User.query.filter_by(email='user1@example.com').first()

        data = [
            Bot(name='Bot 1', args={'arg1': 'value1'}, user_id=user1.id),
        ]

        self.seed(data)
