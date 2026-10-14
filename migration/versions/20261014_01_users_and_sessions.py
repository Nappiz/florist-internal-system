"""Users, revocable sessions, and persistent login throttles.

Revision ID: 20261014_01
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "20261014_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(32), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_superadmin", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("credential_version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.CheckConstraint("length(username) BETWEEN 3 AND 32", name="ck_users_username_length"),
        sa.CheckConstraint("username = lower(username)", name="ck_users_username_lowercase"),
    )
    op.create_index("uq_users_single_superadmin", "users", ["is_superadmin"], unique=True, postgresql_where=sa.text("is_superadmin = true"))
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("credential_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.create_table(
        "login_throttles",
        sa.Column("bucket_key", sa.String(64), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("window_started", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("bucket_key"),
        sa.CheckConstraint("attempts >= 1", name="ck_login_throttles_attempts"),
    )
    op.create_index("ix_login_throttles_window_started", "login_throttles", ["window_started"])
    # Password hashes and session state are backend-only, including when Supabase
    # supplies default table grants to its REST/API roles.
    for table in ("users", "auth_sessions", "login_throttles"):
        op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY')
        op.execute(f'REVOKE ALL ON TABLE public."{table}" FROM PUBLIC, anon, authenticated, service_role')


def downgrade() -> None:
    op.drop_table("login_throttles")
    op.drop_table("auth_sessions")
    op.drop_table("users")
