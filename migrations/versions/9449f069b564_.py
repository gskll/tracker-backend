"""empty message

Revision ID: 9449f069b564
Revises: 
Create Date: 2021-04-16 15:19:44.120367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9449f069b564'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('date_joined', sa.DateTime(), nullable=False),
    sa.Column('last_login', sa.DateTime(), nullable=False),
    sa.Column('role', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('issues',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=False),
    sa.Column('open', sa.Boolean(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('last_modified', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_modified', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('issue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['issue_id'], ['issues.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    op.drop_table('issues')
    op.drop_table('users')
    # ### end Alembic commands ###
