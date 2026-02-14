"""add educational tables

Revision ID: 20260214_edu
Revises: 17a2092b4ddf
Create Date: 2026-02-14 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260214_edu'
down_revision: Union[str, Sequence[str], None] = '17a2092b4ddf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add educational tables."""
    # Create modules table
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('difficulty', sa.String(), nullable=False),
        sa.Column('content_json', sa.Text(), nullable=False),
        sa.Column('quiz_questions_json', sa.Text(), nullable=False),
        sa.Column('exp_reward', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('key_concepts', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_modules_category', 'modules', ['category'])
    op.create_index('idx_modules_difficulty', 'modules', ['difficulty'])

    # Create user_module_progress table
    op.create_table(
        'user_module_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='not_started'),
        sa.Column('completion_percent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quiz_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quiz_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'module_id', name='uq_user_module')
    )
    op.create_index('idx_user_module_user', 'user_module_progress', ['user_id'])
    op.create_index('idx_user_module_module', 'user_module_progress', ['module_id'])

    # Create user_stats table
    op.create_table(
        'user_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_exp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('skill_technical_analysis', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('skill_risk_management', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('skill_psychology', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('skill_market_structure', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.Date(), nullable=True),
        sa.Column('modules_completed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quiz_total_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quiz_correct_answers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_user_stats')
    )
    op.create_index('idx_user_stats_user', 'user_stats', ['user_id'])


def downgrade() -> None:
    """Downgrade schema - remove educational tables."""
    op.drop_table('user_stats')
    op.drop_table('user_module_progress')
    op.drop_table('modules')
