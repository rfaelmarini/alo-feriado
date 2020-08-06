from app import db

class Feriado(db.Model):
    __tablename__ = 'feriados'

    id = db.Column(db.Integer, primary_key=True)
    ibge_code = db.Column(db.Integer)
    name = db.Column(db.String())
    date = db.Column(db.DateTime)

    def __init__(self, ibge_code, name, date):
        self.ibge_code = ibge_code
        self.name = name
        self.date = date

    def __repr__(self):
        return '<id {}>'.format(self.id)
