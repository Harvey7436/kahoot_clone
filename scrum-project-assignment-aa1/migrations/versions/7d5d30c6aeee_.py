"""empty message

Revision ID: 7d5d30c6aeee
Revises: ebc4718e8cb3
Create Date: 2022-09-01 00:15:48.860321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d5d30c6aeee'
down_revision = 'ebc4718e8cb3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quiz', sa.Column('desc', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_quiz_desc'), 'quiz', ['desc'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_quiz_desc'), table_name='quiz')
    op.drop_column('quiz', 'desc')
    # ### end Alembic commands ###