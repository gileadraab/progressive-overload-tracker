"""Refactor Exercise model to use enums and English-only name

Revision ID: 361a12285c98
Revises: ef151a631380
Create Date: 2025-08-08 21:45:51.298998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '361a12285c98'
down_revision: Union[str, Sequence[str], None] = 'ef151a631380'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


categoryenum = postgresql.ENUM(
    'CHEST', 'BACK', 'LEGS', 'SHOULDERS', 'ARMS', 'CORE', name='categoryenum'
)
equipmentenum = postgresql.ENUM(
    'MACHINE', 'DUMBBELL', 'BARBELL', 'BODYWEIGHT', 'KETTLEBELL', 'RESISTANCE_BAND', name='equipmentenum'
)


def upgrade() -> None:
    """Upgrade schema."""
    # Create enums first
    categoryenum.create(op.get_bind(), checkfirst=True)
    equipmentenum.create(op.get_bind(), checkfirst=True)

    # Alter columns to use enums
    op.alter_column(
        'exercises', 'category',
        existing_type=sa.VARCHAR(),
        type_=categoryenum,
        existing_nullable=False,
        postgresql_using='category::text::categoryenum'
    )
    op.alter_column(
        'exercises', 'equipment',
        existing_type=sa.VARCHAR(),
        type_=equipmentenum,
        existing_nullable=True,
        postgresql_using='equipment::text::equipmentenum'
    )

    op.drop_index(op.f('ix_exercises_name_pt'), table_name='exercises')
    op.drop_column('exercises', 'name_pt')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('exercises', sa.Column('name_pt', sa.VARCHAR(), nullable=False))
    op.create_index(op.f('ix_exercises_name_pt'), 'exercises', ['name_pt'], unique=False)

    # Revert columns back to VARCHAR
    op.alter_column(
        'exercises', 'equipment',
        existing_type=equipmentenum,
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using='equipment::text'
    )
    op.alter_column(
        'exercises', 'category',
        existing_type=categoryenum,
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using='category::text'
    )

    # Drop enums after altering columns
    equipmentenum.drop(op.get_bind(), checkfirst=True)
    categoryenum.drop(op.get_bind(), checkfirst=True)
