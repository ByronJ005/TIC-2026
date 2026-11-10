"""create user_roles table and migrate data

Revision ID: 8c3109a47d1e
Revises: 7b209962390c
Create Date: 2026-11-09 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8c3109a47d1e'
down_revision: Union[str, Sequence[str], None] = '7b209962390c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("COMMIT")
        op.execute("ALTER TYPE user_role_enum ADD VALUE IF NOT EXISTS 'SECRETARIA_COOPERATIVA'")
        role_type = postgresql.ENUM(name="user_role_enum", create_type=False)
    else:
        role_type = sa.Enum(
            'ADMIN_GENERAL',
            'ADMIN_COOPERATIVA',
            'SECRETARIA_COOPERATIVA',
            'PASAJERO',
            name='user_role_enum',
        )

    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', role_type, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role')
    )

    # 3. Migrate existing user roles if any
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            INSERT INTO user_roles (user_id, role)
            SELECT id,
                   CASE WHEN role::text = 'SECRETARIA' THEN 'SECRETARIA_COOPERATIVA'::user_role_enum
                        ELSE role
                   END
            FROM users
            ON CONFLICT DO NOTHING
            """
        )
        op.execute(
            """
            INSERT INTO user_roles (user_id, role)
            SELECT id, 'PASAJERO'::user_role_enum
            FROM users
            ON CONFLICT DO NOTHING
            """
        )
    else:
        op.execute(
            """
            INSERT OR IGNORE INTO user_roles (user_id, role)
            SELECT id,
                   CASE WHEN role = 'SECRETARIA' THEN 'SECRETARIA_COOPERATIVA'
                        ELSE role
                   END
            FROM users
            """
        )
        op.execute(
            """
            INSERT OR IGNORE INTO user_roles (user_id, role)
            SELECT id, 'PASAJERO'
            FROM users
            """
        )

    # 4. Drop old column 'role' from users
    op.drop_column('users', 'role')


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        role_type = postgresql.ENUM(name="user_role_enum", create_type=False)
    else:
        role_type = sa.Enum(
            'ADMIN_GENERAL',
            'ADMIN_COOPERATIVA',
            'SECRETARIA_COOPERATIVA',
            'PASAJERO',
            name='user_role_enum',
        )
    op.add_column(
        'users',
        sa.Column('role', role_type, nullable=False, server_default='PASAJERO')
    )
    op.drop_table('user_roles')
