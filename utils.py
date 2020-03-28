import os
import argparse
import pathlib
import code as c

if os.name == 'nt':
    ext, cmd = 'bat','set'
else:
    ext, cmd = 'sh','export'

parser = argparse.ArgumentParser()
parser.add_argument('-n','--name', help='name of the application', required=True)
parser.add_argument('-c', '--components', nargs='+', help='components of the application')
args = parser.parse_args()
pathlib.Path().cwd().joinpath(args.name).mkdir()
project_dir = pathlib.Path().cwd().joinpath(args.name)

