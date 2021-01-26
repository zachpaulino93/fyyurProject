"""empty message

Revision ID: 27343fcc1d69
Revises: ed4207b7271a
Create Date: 2021-01-23 23:21:04.837418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27343fcc1d69'
down_revision = 'ed4207b7271a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
