import pandas as pd
from datetime import datetime, timedelta
from flask import abort, make_response
from models import Feriado
from models import Feriado
from app import db

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
        now = datetime.now()
        date.insert(0, str(now.year))

    return '-'.join(date)

def validate_date(date):
    date = normalize_date(date)
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
    if len(date) == 3:
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
    if not validate_date(date):
        abort(400, 'A data informada e invalida')

    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    splited_date = date.split('-')
    year = splited_date[0]
    month = splited_date[1]
    day = splited_date[2]

    feriado = Feriado.query.filter_by(ibge_code = ibge_code).filter_by(month = month).filter_by(day = day).first()
    if feriado is not None:
        return {'name': feriado.name}

    if len(ibge_code) == 7:
        ibge_code = ibge_code[:2]
        feriado = Feriado.query.filter_by(ibge_code = ibge_code).filter_by(month = month).filter_by(day = day).first()
        if feriado is not None:
            return {'name': feriado.name}

    feriado = get_national_holiday(date)
    if feriado is not None:
        return feriado

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

def save(ibge_code, month, day, name):
    feriado = Feriado.query.filter_by(ibge_code = ibge_code).filter_by(month = month).filter_by(day = day).first()
    if feriado is not None:
        try:
            feriado.name = name
            db.session.commit()
            return make_response('Feriado atualizado com sucesso', 200)
        except:
            abort(500, 'Ocorreu um erro inesperado')
    else:
        try:
            feriado = Feriado(
                ibge_code=ibge_code,
                name=name,
                month=month,
                day=day
            )
            db.session.add(feriado)
            db.session.commit()
            return make_response('Feriado registrado com sucesso', 201)
        except:
            abort(500, 'Ocorreu um erro inesperado')

def save_municipal_state(ibge_code, date, feriado):
    if not validate_date(date):
        abort(400, 'A data informada e invalida')

    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    name = feriado['name']

    splited_date = date.split('-')
    month = splited_date[0]
    day = splited_date[1]

    return save(ibge_code, month, day, name)

def delete(ibge_code, month, day, name):
    date = month + '-' + day
    if name is None:
        feriado = Feriado.query.filter_by(ibge_code = ibge_code).filter_by(month = month).filter_by(day = day).first()
    else:
        feriado = Feriado.query.filter_by(ibge_code = ibge_code).filter_by(month = month).filter_by(day = day).filter_by(name = name).first()

    if feriado is None:
        if len(ibge_code) == 7:
            ibge_code = ibge_code[:2]
            feriado = Feriado.query.filter_by(ibge_code = ibge_code).filter_by(month = month).filter_by(day = day).first()
            if feriado is not None:
                abort(403, 'Nao e possivel remover um feriado estadual em um municipio')
            else:
                feriado = get_national_holiday(date)
                if feriado is not None:
                    abort(403, 'Feriado nacional nao pode ser removido')
                else:
                    abort(404, 'Feriado nao encontrado')
        else:
            feriado = get_national_holiday(date)
            if feriado is not None:
                abort(403, 'Feriado nacional nao pode ser removido')
            else:
                abort(404, 'Feriado nao encontrado')
    else:
        try:
            db.session.delete(feriado)
            db.session.commit()
            return make_response('Feriado removido com sucesso', 204)
        except:
            abort(500, 'Ocorreu um erro inesperado')

def delete_municipal_state(ibge_code, date):
    if not validate_date(date):
        abort(400, 'A data informada e invalida')

    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    splited_date = date.split('-')
    month = splited_date[0]
    day = splited_date[1]

    return delete(ibge_code, month, day, None)

def save_easter(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return save(ibge_code, month, day, "Pascoa")

def delete_easter(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return delete(ibge_code, month, day, "Pascoa")

def save_carnival(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    date = get_carnival_date(date)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return save(ibge_code, month, day, "Carnaval")

def delete_carnival(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    date = get_carnival_date(date)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return delete(ibge_code, month, day, "Carnaval")

def save_corpus_christi(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    date = get_corpus_christi_date(date)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return save(ibge_code, month, day, "Corpus Christi")

def delete_corpus_christi(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    date = get_corpus_christi_date(date)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return delete(ibge_code, month, day, "Corpus Christi")

def save_holy_friday(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    date = get_holy_friday_date(date)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return save(ibge_code, month, day, "Sexta-feira Santa")

def delete_holy_friday(ibge_code):
    if not validate_ibge_code(ibge_code):
        abort(400, 'O codigo do IBGE informado e invalido')

    now = datetime.now()
    date = get_easter_date(now.year)
    date = get_holy_friday_date(date)
    splited_date = date.split('-')
    month = splited_date[1]
    day = splited_date[2]
    return delete(ibge_code, month, day, "Sexta-feira Santa")
