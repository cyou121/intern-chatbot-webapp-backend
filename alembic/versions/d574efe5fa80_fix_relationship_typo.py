"""Fix relationship typo

Revision ID: d574efe5fa80
Revises: 048420c63406
Create Date: 2025-02-13 10:51:21.069623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd574efe5fa80'
down_revision: Union[str, None] = '048420c63406'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('role', sa.Boolean(), nullable=False))
    op.alter_column('messages', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('messages', 'user_or_llm_flag')
    op.alter_column('rooms', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('rooms', 'updated_at')
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=False))
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_column('users', 'password')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('users', 'hashed_password')
    op.add_column('rooms', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.alter_column('rooms', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.add_column('messages', sa.Column('user_or_llm_flag', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.alter_column('messages', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('messages', 'role')
    # ### end Alembic commands ###
