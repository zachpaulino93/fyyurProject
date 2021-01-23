"""empty message

Revision ID: 995793db21ed
Revises: 4c8ccea46c22
Create Date: 2021-01-21 19:35:21.614730

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '995793db21ed'
down_revision = '4c8ccea46c22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
