"""empty message

Revision ID: 3e0775ab464d
Revises: ff6bb08bff05
Create Date: 2024-11-02 10:11:28.005201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e0775ab464d'
down_revision: Union[str, None] = 'ff6bb08bff05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_tokens_id', table_name='tokens')
    op.drop_index('ix_tokens_token', table_name='tokens')
    op.drop_table('tokens')
    op.add_column('orders', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('orders', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'updated_at')
    op.drop_column('orders', 'created_at')
    op.create_table('tokens',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('token', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='tokens_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='tokens_pkey')
    )
    op.create_index('ix_tokens_token', 'tokens', ['token'], unique=True)
    op.create_index('ix_tokens_id', 'tokens', ['id'], unique=False)
    # ### end Alembic commands ###
