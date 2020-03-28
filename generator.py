#Flask mini-generator
import argparse
import pathlib
import os


parser = argparse.ArgumentParser()
parser.add_argument('-n','--name', help='name of the application', required=True)
parser.add_argument('-c', '--components', nargs='+', help='components of the application')
args = parser.parse_args()
pathlib.Path().cwd().joinpath(args.name).mkdir()
project_dir = pathlib.Path().cwd().joinpath(args.name)
wsgi_py = project_dir.joinpath('wsgi.py')
if os.name == 'nt':
    ext,cmd = '.bat','set'
else:
    ext,cmd = '.sh','export'
start = project_dir.joinpath(f'start.{ext}')
with start.open('w', encoding='utf-8') as s:
        s.write(f'{cmd} FLASK_APP=wsgi.py\n{cmd} FLASK_ENV=development\n{cmd} TESTING=False\n{cmd} DEBUG=True\n{cmd} FLASK_DEBUG=1\n{cmd} APP_CONFIG_FILE=config.py\n{cmd} SQLALCHEMY_DATABASE_URI=mysql+mysqlconnector://<user>:<password>@localhost:3306/<dbname>\n{cmd} SQLALCHEMY_TRACK_MODIFICATIONS=False\nflask run\n')
with wsgi_py.open("w", encoding='utf-8') as w:
    w.write('''from application import create_app\napp = create_app()\n\nif __name__ == "__main__":\n\tapp.run(host='0.0.0.0')\n''')
conf_py = project_dir.joinpath('config.py')
with conf_py.open("w", encoding='utf-8') as c:
    c.write('''""""App configuration."""\nfrom os import environ\nfrom dotenv import load_dotenv\n\n
load_dotenv()\n\n"""Flask config class."""\nclass Config:\n\t"""Set Flask configuration vars."""\n\n\t# General Config\n\tTESTING = environ.get("TESTING")\n\tDEBUG = environ.get("DEBUG")\n\n\n\t# Database\n\tSQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")\n\tSQLALCHEMY_TRACK_MODIFICATIONS = environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")\n\n\nclass ProductionConfig(Config):\n\tpass\n\nclass DevelopmentConfig(Config):\n\tDEBUG = True\n\nclass TestingConfig(Config):\n\tTESTING = True''')
project_dir.joinpath('application').mkdir()
app_dir = project_dir.joinpath('application')
app_dir.joinpath('templates').mkdir()
app_dir.joinpath('static').mkdir()
init = app_dir.joinpath('__init__.py')

with init.open('w', encoding='utf-8') as i:
    i.write('''from flask import Flask\nfrom flask_sqlalchemy import SQLAlchemy\nfrom flask_marshmallow import Marshmallow\n\n\n# Globally accessible libraries\ndb = SQLAlchemy()\nma = Marshmallow()\ndef create_app():\n\t"""Initialize the core application."""\n\tapp = Flask(__name__, instance_relative_config=False)\n\tif app.config["ENV"] == "production":\n\t\tapp.config.from_object("config.ProductionConfig")\n\telse:\n\t\tapp.config.from_object("config.DevelopmentConfig")\n\n\tdb.init_app(app)\n\tma.init_app(app)\n\n\twith app.app_context():\n'''+'\n'.join([f'\t\tfrom .{component} import {component}_routes' for component in args.components]) + '\n\n' +'\n'.join([f'\t\tapp.register_blueprint({component}_routes.{component}_bp)' for component in args.components])+'''\n\t\tdb.metadata.clear()\n\t\tdb.create_all()\n\t\treturn app\n''')

models = app_dir.joinpath('models.py')
with models.open('w', encoding='utf-8') as m:
    m.write('from . import db\nfrom . import ma\n\n\n'+"".join([f'class {component.capitalize()}(db.Model):\n\t__tablename__ = \'{component}\'\n\t{component}_id = db.Column(db.Integer,primary_key=True)\n\nclass {component.capitalize()}Schema(ma.ModelSchema):\n\n\tclass Meta:\n\t\tmodel = {component.capitalize()}\n\n\n' for component in args.components]))

for component in args.components:
    app_dir.joinpath(component).mkdir()
    comp_dir = app_dir.joinpath(component)
    comp_dir.joinpath('templates').mkdir()
    r = comp_dir.joinpath(f'{component}_routes.py')
    with r.open("w", encoding="utf-8") as f:
        f.write(f'''from flask import request, Blueprint, render_template, make_response\nfrom ..models import db, {component.capitalize()}, {component.capitalize()}Schema\nfrom datetime import datetime\nfrom flask import current_app as app\nfrom flask import jsonify\nfrom flask_marshmallow import Marshmallow\n\n\n\n# Set up a Blueprint\n{component}_bp = Blueprint('{component}_bp', __name__,\n\t\t\t\t template_folder='templates',\n\t\t\t\t static_folder='static',\n\t\t\t\t url_prefix='/{component}')\n\n\n@{component}_bp.route('/all')\ndef get_{component}s():\n\t"""get {component}s"""\n\t{component}s = db.session.query({component.capitalize()}).all()\n\t{component}_schema = {component.capitalize()}Schema()\n\tresponse = jsonify([{component}_schema.dump({component}) for {component} in {component}s])\n\treturn make_response(response)\n''')


