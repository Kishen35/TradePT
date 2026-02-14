from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, func, ForeignKeyConstraint, UniqueConstraint
from app.config.db import Base

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    difficulty = Column(String, nullable=False, index=True)
    content_json = Column(Text, nullable=False)
    quiz_questions_json = Column(Text, nullable=False)
    exp_reward = Column(Integer, nullable=False, default=50)
    estimated_minutes = Column(Integer, nullable=False, default=5)
    key_concepts = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserModuleProgress(Base):
    __tablename__ = "user_module_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    module_id = Column(Integer, nullable=False, index=True)
    status = Column(String, nullable=False, default="not_started")
    completion_percent = Column(Integer, nullable=False, default=0)
    quiz_score = Column(Integer, nullable=False, default=0)
    quiz_attempts = Column(Integer, nullable=False, default=0)
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        UniqueConstraint('user_id', 'module_id', name='uq_user_module'),
    )


class UserStats(Base):
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    total_exp = Column(Integer, nullable=False, default=0)
    current_level = Column(Integer, nullable=False, default=1)
    skill_technical_analysis = Column(Integer, nullable=False, default=0)
    skill_risk_management = Column(Integer, nullable=False, default=0)
    skill_psychology = Column(Integer, nullable=False, default=0)
    skill_market_structure = Column(Integer, nullable=False, default=0)
    current_streak_days = Column(Integer, nullable=False, default=0)
    longest_streak_days = Column(Integer, nullable=False, default=0)
    last_activity_date = Column(Date, nullable=True)
    modules_completed_count = Column(Integer, nullable=False, default=0)
    quiz_total_attempts = Column(Integer, nullable=False, default=0)
    quiz_correct_answers = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )


class GeneratedQuiz(Base):
    __tablename__ = "generated_quizzes"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, nullable=False, index=True)
    trader_type = Column(String, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    quiz_questions_json = Column(Text, nullable=False)
    ai_generated = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        UniqueConstraint('module_id', 'trader_type', 'user_id', name='uq_module_trader_user'),
    )
