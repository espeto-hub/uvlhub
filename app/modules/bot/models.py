from app import db


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    args = db.Column(db.JSON, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    on_download_dataset = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='bots', lazy=True)

    def __repr__(self):
        return f'{self.name} bot <{self.id}>'
