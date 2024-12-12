from app import db


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    service_name = db.Column(db.String(120), nullable=False)
    service_url = db.Column(db.String(1024), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    on_download_dataset = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='bots', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('name', 'user_id', name='unique_name'),
    )

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'{self.name} bot <{self.id}>'
