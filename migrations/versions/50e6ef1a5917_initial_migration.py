"""Initial migration.

Revision ID: 50e6ef1a5917
Revises: 22425d132bec
Create Date: 2024-08-07 00:34:19.458943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50e6ef1a5917'
down_revision = '22425d132bec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('adrequest', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sent', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('adrequest', schema=None) as batch_op:
        batch_op.drop_column('sent')

    # ### end Alembic commands ###
