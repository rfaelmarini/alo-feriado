import pandas as pd
from datetime import datetime, timedelta
from flask import abort, make_response
from models import Feriado

FERIADOS_NACIONAIS = [
  {'date': '01-01', 'name': 'Ano Novo'},
  {'date': '04-21', 'name': 'Tiradentes'},
  {'date': '05-01', 'name': 'Dia do Trabalhador'},
  {'date': '09-07', 'name': 'Independência'},
  {'date': '10-12', 'name': 'Nossa Senhora Aparecida'},
  {'date': '11-02', 'name': 'Finados'},
  {'date': '11-15', 'name': 'Proclamação da República'},
  {'date': '12-25', 'name': 'Natal'}
]

def normalize_date(date):
    date = date.split('-')
    if len(date) == 2:
        now = datetime.datetime.now()
        date.insert(0, now.year)

    return '-'.join(date)

def validate_date(date):
    try:
        date = date.split('-')
        datetime(int(date[0]), int(date[1]), int(date[2]))
        return True
    except ValueError:
        return False

def validate_ibge_code(ibge_code):
    municipios_df = pd.read_csv("municipios-2019.csv")
    estados_df = pd.read_csv("estados-2019.csv")
    if municipios_df['codigo_ibge'].isin([ibge_code]).any().any() or estados_df['codigo_ibge'].isin([ibge_code]).any().any():
        return True

    return False

def get_national_holiday(date):
    date = date.split('-')
    del(date[0])
    date = '-'.join(date)
    for feriado in FERIADOS_NACIONAIS:
        if feriado['date'] == date:
            return {'name': feriado['name']}

    return None

def get_easter_date(year):
    year = int(year)
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) // 451
    month = (h + L - 7 * m + 114) // 31
    day = 1+ (h + L - 7 * m + 114) % 31
    date = datetime(int(year), int(month), int(day))
    return date.strftime("%Y-%m-%d")

def get_carnival_date(easter_date):
    date = easter_date.split('-')
    date = datetime(int(date[0]), int(date[1]), int(date[2]))
    date = date - timedelta(days = 47)
    return date.strftime("%Y-%m-%d")

def get_corpus_christi_date(easter_date):
    date = easter_date.split('-')
    date = datetime(int(date[0]), int(date[1]), int(date[2]))
    date = date + timedelta(days = 60)
    return date.strftime("%Y-%m-%d")

def get_holy_friday_date(easter_date):
    date = easter_date.split('-')
    date = datetime(int(date[0]), int(date[1]), int(date[2]))
    date = date - timedelta(days = 2)
    return date.strftime("%Y-%m-%d")

def fetch(ibge_code, date):
    date = normalize_date(date)
    if not validate_date(date):
        abort(400, 'A data informada e invalida')

    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    feriado = Feriado.query.filter_by(ibge_code = ibge_code).filter_by(date = date).first()
    if feriado is not None:
        return feriado

    feriado = get_national_holiday(date)
    if feriado is not None:
        return feriado

    year = date.split('-')[0]
    easter_date = get_easter_date(year)
    if date == easter_date:
        return {'name': 'Pascoa'}

    if date == get_carnival_date(easter_date):
        return {'name': 'Carnaval'}

    if date == get_corpus_christi_date(easter_date):
        return {'name': 'Corpus Christi'}

    if date == get_holy_friday_date(easter_date):
        return {'name': 'Sexta-feira Santa'}

    abort(404, 'Feriado nao encontrado')

