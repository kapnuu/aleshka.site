"""empty message

Revision ID: 4665e6b437e4
Revises: 0e4f9bbc0c44
Create Date: 2020-11-15 01:11:48.970714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4665e6b437e4'
down_revision = '0e4f9bbc0c44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('thumbnail', sa.Column('data', sa.BLOB(), nullable=True))
    op.drop_column('thumbnail', 'b64data')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('thumbnail', sa.Column('b64data', sa.TEXT(), nullable=True))
    op.drop_column('thumbnail', 'data')
    # ### end Alembic commands ###