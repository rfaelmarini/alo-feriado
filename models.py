from app import db

class Feriado(db.Model):
    __tablename__ = 'feriados'

    id = db.Column(db.Integer, primary_key=True)
    ibge_code = db.Column(db.Integer)
    name = db.Column(db.String())
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)

    def __init__(self, ibge_code, name, month, day):
        self.ibge_code = ibge_code
        self.name = name
        self.month = month
        self.day = day

    def __repr__(self):
        return '<id {}>'.format(self.id)
