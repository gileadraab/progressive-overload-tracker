"""add authentication fields to user model

Revision ID: ca2890303be8
Revises: be0a97f219e8
Create Date: 2025-10-21 21:12:21.353714

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ca2890303be8"
down_revision: Union[str, Sequence[str], None] = "be0a97f219e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add authentication fields to existing users table
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.String(), nullable=True))
    op.add_column("users", sa.Column("oauth_provider", sa.String(), nullable=True))
    op.add_column("users", sa.Column("oauth_id", sa.String(), nullable=True))

    # Create indexes for new fields
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Make email NOT NULL after backfilling (if needed in future)
    # For now, keeping nullable=True for existing records


def downgrade() -> None:
    """Downgrade schema."""
    # Remove authentication fields from users table
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "oauth_id")
    op.drop_column("users", "oauth_provider")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "email")
