from app import create_app, db, cli
from app.models import Visitor, Cat

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Visitor': Visitor, 'Cat': Cat}

# set FLASK_APP=aleshka.py

# if problems with db:
#
# flask db stamp head
# flask db migrate
# flask db upgrade
