"""empty message

Revision ID: 74b469adef82
Revises: 6876763e1a97
Create Date: 2022-09-20 00:14:55.180043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74b469adef82'
down_revision = '6876763e1a97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_question_desc', table_name='question')
    op.create_index(op.f('ix_question_desc'), 'question', ['desc'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_question_desc'), table_name='question')
    op.create_index('ix_question_desc', 'question', ['desc'], unique=False)
    # ### end Alembic commands ###