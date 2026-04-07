"""Add password reset tokens

Revision ID: b9d0c5a1e0f1
Revises: 8258de3b8189
Create Date: 2026-01-25 10:36:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9d0c5a1e0f1'
down_revision: Union[str, Sequence[str], None] = '8258de3b8189'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Em dev, o app pode ter criado a tabela via `Base.metadata.create_all()`.
    # Tornamos a migration idempotente para evitar falha de "table already exists".
    exists = bind.execute(
        sa.text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='password_reset_tokens'"
        )
    ).fetchone()

    if not exists:
        op.create_table(
            'password_reset_tokens',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('token', sa.String(), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('used_at', sa.DateTime(), nullable=True),
            sa.Column(
                'created_at',
                sa.DateTime(),
                server_default=sa.text('(CURRENT_TIMESTAMP)'),
                nullable=True,
            ),
        )

    # Garante o índice único do token (SQLite: nome do índice aparece no sqlite_master).
    idx_exists = bind.execute(
        sa.text(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='ix_password_reset_tokens_token'"
        )
    ).fetchone()
    if not idx_exists:
        op.create_index(
            'ix_password_reset_tokens_token',
            'password_reset_tokens',
            ['token'],
            unique=True,
        )


def downgrade() -> None:
    op.drop_index('ix_password_reset_tokens_token', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
