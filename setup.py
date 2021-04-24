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
    url='https://github.com/noelcody/termchess',
    license='',
    author='noel cody',
    author_email='',
    description='',
    app=APP,
    data_files=DATA_FILES,
    setup_requires=['py2app'],
    install_requires=['bearlibterminal', 'numpy', 'stockfish'],
    options={'py2app': OPTIONS},
)
