"""empty message

Revision ID: 9e8c4ceed2e4
Revises: c48e8b90b0c6
Create Date: 2024-03-28 16:02:53.423224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e8c4ceed2e4'
down_revision = 'c48e8b90b0c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fighter_table', sa.Column('image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fighter_table', 'image')
    # ### end Alembic commands ###
