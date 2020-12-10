import os


def register(app):
    @app.cli.group()
    def requirements():
        """Commands to manage requirements.txt file."""
        pass

    @requirements.command()
    def freeze():
        """Freeze all project requirements to requirements.txt file."""
        if os.system('pip freeze > requirements.txt'):
            raise RuntimeError('freeze command failed')

    @requirements.command()
    def install():
        """Install all project requirements."""
        if os.system('pip install -r requirements.txt'):
            raise RuntimeError('freeze command failed')

    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    '''
    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')
    '''
