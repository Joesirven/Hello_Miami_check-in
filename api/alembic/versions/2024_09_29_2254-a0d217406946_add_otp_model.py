"""Add OTP model

Revision ID: a0d217406946
Revises: 0b243b20af6f
Create Date: 2024-09-29 22:54:25.173563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0d217406946'
down_revision: Union[str, None] = '0b243b20af6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'otps',
        sa.Column('otp_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('channel', sa.String(), nullable=True),
        sa.Column('status', sa.Enum(
            'PENDING',
            'VERIFIED',
            'FAILED',
            name='otpstatus'
        ), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('verification_sid', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.contact_id'], ),
        sa.PrimaryKeyConstraint('otp_id')
    )
    op.create_index(
        op.f('ix_otps_contact_id'),
        'otps',
        ['contact_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_otps_otp_id'),
        'otps',
        ['otp_id'],
        unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_otps_otp_id'), table_name='otps')
    op.drop_index(op.f('ix_otps_contact_id'), table_name='otps')
    op.drop_table('otps')
    # ### end Alembic commands ###
