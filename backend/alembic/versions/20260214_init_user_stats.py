"""init user stats for existing users

Revision ID: 20260214_init_stats
Revises: 20260214_edu
Create Date: 2026-02-14 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '20260214_init_stats'
down_revision: Union[str, Sequence[str], None] = '20260214_edu'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Initialize UserStats for all existing users."""
    # Create a temporary table reference
    users = table('users', column('id', sa.Integer))
    user_stats = table('user_stats',
        column('user_id', sa.Integer),
        column('total_exp', sa.Integer),
        column('current_level', sa.Integer),
        column('skill_technical_analysis', sa.Integer),
        column('skill_risk_management', sa.Integer),
        column('skill_psychology', sa.Integer),
        column('skill_market_structure', sa.Integer),
        column('current_streak_days', sa.Integer),
        column('longest_streak_days', sa.Integer),
        column('last_activity_date', sa.Date),
        column('modules_completed_count', sa.Integer),
        column('quiz_total_attempts', sa.Integer),
        column('quiz_correct_answers', sa.Integer)
    )
    
    # Get connection
    conn = op.get_bind()
    
    # Get all existing user IDs
    result = conn.execute(sa.text("SELECT id FROM users"))
    user_ids = [row[0] for row in result]
    
    # Insert UserStats for each user
    for user_id in user_ids:
        # Check if stats already exist
        existing = conn.execute(
            sa.text("SELECT id FROM user_stats WHERE user_id = :uid"),
            {"uid": user_id}
        ).fetchone()
        
        if not existing:
            conn.execute(
                sa.text("""
                    INSERT INTO user_stats 
                    (user_id, total_exp, current_level, skill_technical_analysis, 
                     skill_risk_management, skill_psychology, skill_market_structure,
                     current_streak_days, longest_streak_days, modules_completed_count,
                     quiz_total_attempts, quiz_correct_answers)
                    VALUES (:uid, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                """),
                {"uid": user_id}
            )


def downgrade() -> None:
    """Remove initialized UserStats (only those with 0 exp)."""
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM user_stats WHERE total_exp = 0 AND modules_completed_count = 0")
    )
