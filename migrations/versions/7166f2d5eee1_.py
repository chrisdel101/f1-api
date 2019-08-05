"""empty message

Revision ID: 7166f2d5eee1
Revises: 22a93e84353b
Create Date: 2019-08-05 17:23:01.227297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7166f2d5eee1'
down_revision = '22a93e84353b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('team')
    op.drop_table('driver')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('driver',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('driver_name', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
    sa.Column('country', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('name_slug', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
    sa.Column('date_of_birth', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('driver_number', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('place_of_birth', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('flag_img_url', sa.VARCHAR(length=150), autoincrement=False, nullable=True),
    sa.Column('main_image', sa.VARCHAR(length=150), autoincrement=False, nullable=True),
    sa.Column('podiums', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('points', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('world_championships', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('team', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('highest_grid_position', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='driver_pkey'),
    sa.UniqueConstraint('driver_name', name='driver_driver_name_key'),
    sa.UniqueConstraint('name_slug', name='driver_name_slug_key')
    )
    op.create_table('team',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name_slug', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('url_name_slug', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('full_team_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('base', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('team_chief', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('technical_chief', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('power_unit', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('first_team_entry', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('highest_race_finish', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('pole_positions', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('fastest_laps', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
    sa.Column('main_image', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('flag_img_url', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('logo_url', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='team_pkey'),
    sa.UniqueConstraint('full_team_name', name='team_full_team_name_key')
    )
    # ### end Alembic commands ###
