from core.seeders.BaseSeeder import BaseSeeder
from app.modules.fakenodo.models import Fakenodo


class FakenodoSeeder(BaseSeeder):
    def run(self):
        data = [
            Fakenodo(id=1),
            Fakenodo(id=2),
            Fakenodo(id=3)
        ]
        self.seed(data)
