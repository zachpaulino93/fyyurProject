"""empty message

Revision ID: 69509b7b4a31
Revises: 2402f10ed7d4
Create Date: 2021-01-25 19:50:46.156322

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '69509b7b4a31'
down_revision = '2402f10ed7d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_genre_table',
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.PrimaryKeyConstraint('genre_id', 'artist_id')
    )
    op.create_table('venue_genre_table',
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('genre_id', 'venue_id')
    )
    op.drop_column('artist', 'genres')
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=False))
    op.add_column('artist', sa.Column('genres', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=False))
    op.drop_table('venue_genre_table')
    op.drop_table('artist_genre_table')
    op.drop_table('genre')
    # ### end Alembic commands ###
