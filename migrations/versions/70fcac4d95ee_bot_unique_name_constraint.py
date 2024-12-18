"""bot_unique_name_constraint

Revision ID: 70fcac4d95ee
Revises: f0cd18e12ccc
Create Date: 2024-12-12 09:03:50.322066

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '70fcac4d95ee'
down_revision = 'f0cd18e12ccc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot', schema=None) as batch_op:
        batch_op.create_unique_constraint('unique_name', ['name', 'user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot', schema=None) as batch_op:
        batch_op.drop_constraint('unique_name', type_='unique')

    # ### end Alembic commands ###
