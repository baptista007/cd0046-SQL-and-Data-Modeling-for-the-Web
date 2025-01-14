"""Additional fields for venue

Revision ID: 8460125bebf6
Revises: f60dd0763db9
Create Date: 2022-08-13 17:10:57.476113

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8460125bebf6'
down_revision = 'f60dd0763db9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
