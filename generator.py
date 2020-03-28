#Flask mini-generator
import argparse
import pathlib
import os
from code import start_code, wsgi_code, conf_code, init_code, models_code, comp_f
from utils import project_dir, args, ext


wsgi_py = project_dir.joinpath('wsgi.py')
start = project_dir.joinpath(f'start.{ext}')
with start.open('w', encoding='utf-8') as s:
        s.write(start_code)
with wsgi_py.open("w", encoding='utf-8') as w:
    w.write(wsgi_code)
conf_py = project_dir.joinpath('config.py')
with conf_py.open("w", encoding='utf-8') as c:
    c.write(conf_code)
project_dir.joinpath('application').mkdir()
app_dir = project_dir.joinpath('application')
app_dir.joinpath('templates').mkdir()
app_dir.joinpath('static').mkdir()
init = app_dir.joinpath('__init__.py')

with init.open('w', encoding='utf-8') as i:
    i.write(init_code)

models = app_dir.joinpath('models.py')
with models.open('w', encoding='utf-8') as m:
    m.write(models_code)

for component in args.components:
    app_dir.joinpath(component).mkdir()
    comp_dir = app_dir.joinpath(component)
    comp_dir.joinpath('templates').mkdir()
    r = comp_dir.joinpath(f'{component}_routes.py')
    with r.open("w", encoding="utf-8") as f:
        f.write(comp_f(component))


