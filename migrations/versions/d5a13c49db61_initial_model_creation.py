"""initial model creation

Revision ID: d5a13c49db61
Revises: 
Create Date: 2022-02-22 19:16:32.218339

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'd5a13c49db61'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('image',
    sa.Column('entity_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.Column('image', sa.LargeBinary(), nullable=False),
    sa.Column('file_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('mime_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('file_name'),
    sa.UniqueConstraint('image')
    )
    op.create_table('item',
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('artist', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('admin', sa.Boolean(), nullable=False),
    sa.Column('entity_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('playlist',
    sa.Column('entity_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('spotify', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('amazon', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('apple_music', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('release_date', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('playlistitemlink',
    sa.Column('playlist_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.ForeignKeyConstraint(['playlist_id'], ['playlist.id'], ),
    sa.PrimaryKeyConstraint('playlist_id', 'item_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('playlistitemlink')
    op.drop_table('playlist')
    op.drop_table('user')
    op.drop_table('item')
    op.drop_table('image')
    op.drop_table('category')
    # ### end Alembic commands ###