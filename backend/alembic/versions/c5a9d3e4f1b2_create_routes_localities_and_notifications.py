"""create routes localities and notifications

Revision ID: c5a9d3e4f1b2
Revises: b4f8c9d1e2f3
Create Date: 2026-11-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5a9d3e4f1b2'
down_revision: Union[str, Sequence[str], None] = 'b4f8c9d1e2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create localities table
    op.create_table(
        'localities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
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
        sa.CheckConstraint('length(trim(name)) >= 1', name='ck_localities_name_min_length'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_localities_id'), 'localities', ['id'], unique=False)
    op.create_index(
        'uq_localities_lower_name',
        'localities',
        [sa.text('lower(name)')],
        unique=True,
    )

    # 2. Create routes table
    op.create_table(
        'routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cooperativa_id', sa.Integer(), nullable=True),
        sa.Column('origin_id', sa.Integer(), nullable=False),
        sa.Column('destination_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('name_suffix', sa.String(length=30), nullable=True),
        sa.Column('distance_km', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('estimated_time_minutes', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=100), nullable=True),
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
        sa.CheckConstraint('origin_id <> destination_id', name='ck_routes_origin_destination_diff'),
        sa.CheckConstraint('distance_km > 0', name='ck_routes_distance_positive'),
        sa.CheckConstraint(
            'estimated_time_minutes >= 1 AND estimated_time_minutes <= 1439',
            name='ck_routes_time_range',
        ),
        sa.ForeignKeyConstraint(['cooperativa_id'], ['cooperatives.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['origin_id'], ['localities.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['destination_id'], ['localities.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_routes_id'), 'routes', ['id'], unique=False)
    op.create_index(op.f('ix_routes_cooperativa_id'), 'routes', ['cooperativa_id'], unique=False)
    op.create_index(op.f('ix_routes_origin_id'), 'routes', ['origin_id'], unique=False)
    op.create_index(op.f('ix_routes_destination_id'), 'routes', ['destination_id'], unique=False)
    op.create_index(
        'uq_general_routes_origin_dest_dist',
        'routes',
        ['origin_id', 'destination_id', 'distance_km'],
        unique=True,
        postgresql_where=sa.text('cooperativa_id IS NULL'),
    )
    op.create_index(
        'uq_coop_routes_coop_origin_dest_dist',
        'routes',
        ['cooperativa_id', 'origin_id', 'destination_id', 'distance_km'],
        unique=True,
        postgresql_where=sa.text('cooperativa_id IS NOT NULL'),
    )

    # 3. Create route_stops table
    op.create_table(
        'route_stops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('locality_id', sa.Integer(), nullable=False),
        sa.Column('stop_order', sa.Integer(), nullable=False),
        sa.CheckConstraint('stop_order >= 1', name='ck_route_stops_order_positive'),
        sa.ForeignKeyConstraint(['locality_id'], ['localities.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('route_id', 'stop_order', name='uq_route_stops_route_order'),
        sa.UniqueConstraint('route_id', 'locality_id', name='uq_route_stops_route_locality'),
    )
    op.create_index(op.f('ix_route_stops_id'), 'route_stops', ['id'], unique=False)
    op.create_index(op.f('ix_route_stops_locality_id'), 'route_stops', ['locality_id'], unique=False)
    op.create_index(op.f('ix_route_stops_route_id'), 'route_stops', ['route_id'], unique=False)

    # 4. Create cooperativa_general_routes table
    op.create_table(
        'cooperativa_general_routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cooperativa_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(['cooperativa_id'], ['cooperatives.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cooperativa_id', 'route_id', name='uq_coop_general_routes_coop_route'),
    )
    op.create_index(op.f('ix_cooperativa_general_routes_id'), 'cooperativa_general_routes', ['id'], unique=False)
    op.create_index(
        op.f('ix_cooperativa_general_routes_cooperativa_id'),
        'cooperativa_general_routes',
        ['cooperativa_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_cooperativa_general_routes_route_id'),
        'cooperativa_general_routes',
        ['route_id'],
        unique=False,
    )

    # 5. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(
        'ix_notifications_user_created',
        'notifications',
        ['user_id', sa.text('created_at DESC')],
        unique=False,
    )


def downgrade() -> None:
    # 5. Drop notifications
    op.drop_index('ix_notifications_user_created', table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')

    # 4. Drop cooperativa_general_routes
    op.drop_index(op.f('ix_cooperativa_general_routes_route_id'), table_name='cooperativa_general_routes')
    op.drop_index(op.f('ix_cooperativa_general_routes_cooperativa_id'), table_name='cooperativa_general_routes')
    op.drop_index(op.f('ix_cooperativa_general_routes_id'), table_name='cooperativa_general_routes')
    op.drop_table('cooperativa_general_routes')

    # 3. Drop route_stops
    op.drop_index(op.f('ix_route_stops_route_id'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_locality_id'), table_name='route_stops')
    op.drop_index(op.f('ix_route_stops_id'), table_name='route_stops')
    op.drop_table('route_stops')

    # 2. Drop routes
    op.drop_index('uq_coop_routes_coop_origin_dest_dist', table_name='routes')
    op.drop_index('uq_general_routes_origin_dest_dist', table_name='routes')
    op.drop_index(op.f('ix_routes_destination_id'), table_name='routes')
    op.drop_index(op.f('ix_routes_origin_id'), table_name='routes')
    op.drop_index(op.f('ix_routes_cooperativa_id'), table_name='routes')
    op.drop_index(op.f('ix_routes_id'), table_name='routes')
    op.drop_table('routes')

    # 1. Drop localities
    op.drop_index('uq_localities_lower_name', table_name='localities')
    op.drop_index(op.f('ix_localities_id'), table_name='localities')
    op.drop_table('localities')
