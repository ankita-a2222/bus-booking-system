"""Initial database setup

Revision ID: 1a01a0a1a1a1
Revises: 
Create Date: 2023-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a01a0a1a1a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create buses table
    op.create_table('buses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create routes table
    op.create_table('routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('from_location', sa.String(length=100), nullable=False),
        sa.Column('to_location', sa.String(length=100), nullable=False),
        sa.Column('departure_time', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('bus_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['bus_id'], ['buses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create seats table
    op.create_table('seats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, default=True),
        sa.Column('bus_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['bus_id'], ['buses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create passengers table
    op.create_table('passengers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create bookings table
    op.create_table('bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_date', sa.DateTime(), nullable=True),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('payment_status', sa.String(length=20), nullable=True),
        sa.Column('passenger_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('seat_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['passenger_id'], ['passengers.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.ForeignKeyConstraint(['seat_id'], ['seats.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('bookings')
    op.drop_table('passengers')
    op.drop_table('seats')
    op.drop_table('routes')
    op.drop_table('buses')
