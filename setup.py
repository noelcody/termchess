# http://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/

from setuptools import setup

APP = ['main.py']
DATA_FILES = ['CASEFONT.TTF', 'libBearLibTerminal.dylib', 'stockfish']
OPTIONS = {
    'iconfile': 'app.icns'
}

setup(
    name='TermChess',
    version='',
    packages=['engine', 'engine.map', 'engine.map.util', 'engine.map.components', 'engine.input', 'engine.render'],
    url='',
    license='',
    author='',
    author_email='',
    description='',
    app=APP,
    data_files=DATA_FILES,
    setup_requires=['py2app'],
    install_requires=['bearlibterminal', 'numpy', 'stockfish'],
    options={'py2app': OPTIONS},
)
