from app.modules.auth.models import User
from core.seeders.BaseSeeder import BaseSeeder
from app.modules.bot.models import Bot


class BotSeeder(BaseSeeder):

    def run(self):
        user1 = User.query.filter_by(email='user1@example.com').first()

        data = [
            Bot(name='Bot 1', service_name='Discord', service_url='discord://webhook_id/webhook_token', user_id=user1.id),
        ]

        self.seed(data)
