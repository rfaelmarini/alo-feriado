import os
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask import redirect

basedir = os.path.abspath(os.path.dirname(__file__))

connex_app = connexion.App(__name__, specification_dir=basedir)

app = connex_app.app
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

connex_app.add_api('swagger.yaml')

@app.route('/')
def index():
    return redirect('/ui')

if __name__ == '__main__':
    app.run()
