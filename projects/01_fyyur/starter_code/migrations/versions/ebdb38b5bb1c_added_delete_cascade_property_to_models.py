"""Added delete cascade property to models

Revision ID: ebdb38b5bb1c
Revises: ff5ab0313587
Create Date: 2021-04-02 18:38:09.209632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebdb38b5bb1c'
down_revision = 'ff5ab0313587'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###
