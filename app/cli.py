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
