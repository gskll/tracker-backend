"""empty message

Revision ID: 0eb7d84d7591
Revises: 4e087f4bfb10
Create Date: 2021-04-20 01:00:33.974851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0eb7d84d7591'
down_revision = '4e087f4bfb10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('issue_id', sa.Integer(), nullable=False))
    op.add_column('comments', sa.Column('user_id', sa.String(), nullable=False))
    op.drop_constraint('comments_user_fkey', 'comments', type_='foreignkey')
    op.drop_constraint('comments_issue_fkey', 'comments', type_='foreignkey')
    op.create_foreign_key(None, 'comments', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'comments', 'issues', ['issue_id'], ['id'])
    op.drop_column('comments', 'user')
    op.drop_column('comments', 'issue')
    op.add_column('issues', sa.Column('user_id', sa.String(), nullable=False))
    op.drop_constraint('issues_user_fkey', 'issues', type_='foreignkey')
    op.create_foreign_key(None, 'issues', 'users', ['user_id'], ['id'])
    op.drop_column('issues', 'user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('issues', sa.Column('user', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'issues', type_='foreignkey')
    op.create_foreign_key('issues_user_fkey', 'issues', 'users', ['user'], ['id'])
    op.drop_column('issues', 'user_id')
    op.add_column('comments', sa.Column('issue', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('comments', sa.Column('user', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.create_foreign_key('comments_issue_fkey', 'comments', 'issues', ['issue'], ['id'])
    op.create_foreign_key('comments_user_fkey', 'comments', 'users', ['user'], ['id'])
    op.drop_column('comments', 'user_id')
    op.drop_column('comments', 'issue_id')
    # ### end Alembic commands ###
