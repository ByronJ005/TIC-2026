"""create cooperatives and audit logs

Revision ID: b4f8c9d1e2f3
Revises: a1f4c2d9b7e3
Create Date: 2026-11-11 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4f8c9d1e2f3'
down_revision: Union[str, Sequence[str], None] = 'a1f4c2d9b7e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create cooperatives table
    op.create_table(
        'cooperatives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('ruc', sa.String(length=13), nullable=False),
        sa.Column('address', sa.String(length=150), nullable=True),
        sa.Column('phone', sa.String(length=10), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.CheckConstraint('length(ruc) = 13', name='ck_cooperatives_ruc_length'),
        sa.CheckConstraint('length(name) >= 1', name='ck_cooperatives_name_min_length'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ruc', name='uq_cooperatives_ruc'),
    )
    op.create_index(op.f('ix_cooperatives_id'), 'cooperatives', ['id'], unique=False)
    op.create_index(op.f('ix_cooperatives_ruc'), 'cooperatives', ['ruc'], unique=True)
    op.create_index(
        'uq_cooperatives_lower_name',
        'cooperatives',
        [sa.text('lower(name)')],
        unique=True,
    )

    # 2. Add cooperativa_id to users
    op.add_column('users', sa.Column('cooperativa_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_users_cooperativa_id'), 'users', ['cooperativa_id'], unique=False)
    op.create_foreign_key(
        'fk_users_cooperativa_id_cooperatives',
        'users',
        'cooperatives',
        ['cooperativa_id'],
        ['id'],
        ondelete='SET NULL',
    )

    # 3. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('entity', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('result', sa.String(length=20), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_module'), 'audit_logs', ['module'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    # 3. Drop audit_logs table
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_module'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

    # 2. Remove cooperativa_id from users
    op.drop_constraint('fk_users_cooperativa_id_cooperatives', 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_cooperativa_id'), table_name='users')
    op.drop_column('users', 'cooperativa_id')

    # 1. Drop cooperatives table
    op.drop_index('uq_cooperatives_lower_name', table_name='cooperatives')
    op.drop_index(op.f('ix_cooperatives_ruc'), table_name='cooperatives')
    op.drop_index(op.f('ix_cooperatives_id'), table_name='cooperatives')
    op.drop_table('cooperatives')

