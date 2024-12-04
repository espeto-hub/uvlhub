from app import db


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'Bot<{self.id}>'
