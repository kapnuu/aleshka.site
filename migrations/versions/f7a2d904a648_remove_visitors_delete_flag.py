"""remove visitors delete flag

Revision ID: f7a2d904a648
Revises: d28cc7b0ccf4
Create Date: 2020-11-25 23:01:28.179468

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7a2d904a648'
down_revision = 'd28cc7b0ccf4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('visitor', 'deleted')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('visitor', sa.Column('deleted', sa.BOOLEAN(), nullable=True))
    # ### end Alembic commands ###
