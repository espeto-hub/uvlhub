"""Agregando columnas user_id y created_at a dataset_ratings

Revision ID: fe893c367baa
Revises: dc5d8575a85e
Create Date: 2024-11-22 12:19:45.728310

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fe893c367baa'
down_revision = 'dc5d8575a85e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dataset_ratings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_unique_constraint('uix_dataset_user', ['dataset_id', 'user_id'])
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dataset_ratings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', mysql.DATETIME(), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint('uix_dataset_user', type_='unique')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###