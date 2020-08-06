"""empty message

Revision ID: b2976993e1be
Revises: f30f7d001cef
Create Date: 2020-08-06 17:11:47.827856

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2976993e1be'
down_revision = 'f30f7d001cef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feriados', sa.Column('day', sa.Integer(), nullable=True))
    op.add_column('feriados', sa.Column('month', sa.Integer(), nullable=True))
    op.drop_column('feriados', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('feriados', sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('feriados', 'month')
    op.drop_column('feriados', 'day')
    # ### end Alembic commands ###
