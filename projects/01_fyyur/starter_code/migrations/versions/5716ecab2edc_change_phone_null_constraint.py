"""change phone null constraint

Revision ID: 5716ecab2edc
Revises: ebdb38b5bb1c
Create Date: 2021-04-02 18:41:38.098050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5716ecab2edc'
down_revision = 'ebdb38b5bb1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###