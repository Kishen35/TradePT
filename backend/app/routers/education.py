"""
Education System API Router
Handles module retrieval, progress tracking, and educational analysis
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
import json

from app.config.db import get_db, engine
from app.database.model.modules import Module, UserModuleProgress, UserStats, GeneratedQuiz
from app.database.models.users import User
from app.services.deriv.knowledge_base import get_module_for_pattern, get_product_info
from app.services.ai.llm.education.educational_analysis_prompts import (
    build_buy_analysis_prompt,
    build_close_analysis_prompt,
    UNIFIED_ANALYSIS_SYSTEM_PROMPT
)
from app.config.ai_config import get_ai_settings
from app.services.ai.llm.education.module_generator import get_module_generator, MODULES
from app.ai_services.deriv_market import get_market_service
from app.ai_services.analysis import detect_patterns
from anthropic import Anthropic
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/education", tags=["Education"])

# Auto-create tables and seed modules on import
from app.config.db import Base
Base.metadata.create_all(bind=engine)

# Seed modules table if empty
from sqlalchemy.orm import Session as DBSession
with DBSession(engine) as _db:
    if _db.query(Module).count() == 0:
        for m in MODULES:
            _db.add(Module(
                id=m["id"], title=m["title"], category=m["category"],
                difficulty="beginner",
                content_json=json.dumps({"focus": m.get("momentum_focus", "")}),
                quiz_questions_json=json.dumps([]),
                exp_reward=m["exp_reward"], estimated_minutes=m["estimated_minutes"],
                key_concepts=",".join(m.get("key_concepts", [])),
            ))
        _db.commit()


# ============ REQUEST/RESPONSE MODELS ============

class EducationalAnalysisRequest(BaseModel):
    """Request for AI analysis on trade decision"""
    user_id: int
    action_type: str = Field(..., pattern="^(buy_analysis|close_analysis)$")
    symbol: str
    stake: Optional[float] = None
    balance: float
    trade_type: Optional[str] = None
    market_type: Optional[str] = None  # e.g. "Volatility 100 (1s) Index"
    trend_type: Optional[str] = None   # "up", "down", "sideways"
    parameters: Optional[dict] = None
    # For close analysis
    pnl: Optional[float] = None
    entry_price: Optional[float] = None
    current_price: Optional[float] = None
    duration_minutes: Optional[int] = None


class EducationalAnalysisResponse(BaseModel):
    """Response with educational analysis and module recommendation"""
    analysis_text: str
    recommended_module_id: Optional[int] = None
    recommended_module_title: Optional[str] = None
    detected_patterns: List[str] = []
    urgency: str = "medium"  # low, medium, high, critical


class ModuleResponse(BaseModel):
    """Single module data"""
    id: int
    title: str
    category: str
    difficulty: str
    estimated_minutes: int
    exp_reward: int
    key_concepts: str
    progress: Optional[dict] = None  # User's progress on this module


class QuizSubmissionRequest(BaseModel):
    """Quiz answer submission"""
    user_id: int
    module_id: int
    answers: List[str]  # ["A", "B"] for 2 questions


class QuizSubmissionResponse(BaseModel):
    """Quiz results"""
    score: int  # 0-100
    correct_count: int
    total_questions: int
    exp_earned: int
    passed: bool
    explanations: List[dict]


class ProgressResponse(BaseModel):
    """User's overall progress"""
    total_exp: int
    current_level: int
    current_streak_days: int
    skill_scores: dict
    modules_completed: int
    total_modules: int
    category_progress: dict


# ============ ENDPOINTS ============

@router.post("/analyze", response_model=EducationalAnalysisResponse)
async def analyze_trade_decision(
    request: EducationalAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Provide educational analysis when user clicks AI Analysis button
    
    This is triggered when user clicks:
    - "AI Analysis" button on BUY screen
    - "AI" button on CLOSE/SELL screen
    """
    try:
        # Get user profile
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_profile = {
            "experience_level": user.experience_level,
            "trading_style": user.trading_duration,
            "risk_tolerance": user.risk_tolerance
        }
        
        # Get recent trades and patterns from Deriv
        market_service = get_market_service()

        recent_trades = await market_service.get_recent_trades(limit=10)
        patterns = detect_patterns(recent_trades)
        detected_pattern_names = [p.pattern.value if hasattr(p.pattern, 'value') else str(p.pattern) for p in patterns if p.detected]
        
        # Get product info for context
        product_info = get_product_info(request.trade_type or "general")
        
        # Build appropriate prompt
        if request.action_type == "buy_analysis":
            trade_setup = {
                "symbol": request.symbol,
                "stake": request.stake or 0,
                "balance": request.balance,
                "trade_type": request.trade_type,
                "market_type": request.market_type,
                "trend_type": request.trend_type,
                "parameters": request.parameters or {},
            }
            
            user_prompt = build_buy_analysis_prompt(
                user_profile=user_profile,
                trade_setup=trade_setup,
                recent_trades=recent_trades,
                detected_patterns=patterns,
                deriv_product_info=product_info
            )
        else:  # close_analysis
            open_position = {
                "symbol": request.symbol,
                "pnl": request.pnl,
                "duration_minutes": request.duration_minutes,
                "entry_price": request.entry_price,
                "current_price": request.current_price,
                "balance": request.balance
            }
            
            user_prompt = build_close_analysis_prompt(
                user_profile=user_profile,
                open_position=open_position,
                recent_trades=recent_trades,
                detected_patterns=patterns
            )
        
        # Call Claude API for analysis
        settings = get_ai_settings()
        anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
        
        response = anthropic_client.messages.create(
            model=settings.anthropic_model_name,
            max_tokens=1024,
            system=UNIFIED_ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        analysis_text = response.content[0].text
        
        # Find recommended module based on detected patterns
        recommended_module = None
        recommended_title = None
        urgency = "medium"
        
        if detected_pattern_names:
            # Get highest priority pattern
            for pattern_name in detected_pattern_names:
                module_info = get_module_for_pattern(pattern_name)
                if module_info:
                    # Find module in database
                    module = db.query(Module).filter(
                        Module.title == module_info['module_title']
                    ).first()

                    if module:
                        recommended_module = module.id
                        recommended_title = module.title
                        urgency = module_info.get('urgency', 'medium')
                        break

        # Fallback: recommend a module based on action type if none from patterns
        if recommended_module is None:
            fallback_map = {
                "buy_analysis": {"category": "Risk_Management"},
                "close_analysis": {"category": "Psychology"},
            }
            fallback = fallback_map.get(request.action_type, {"category": "Technical_Analysis"})
            fallback_module = db.query(Module).filter(
                Module.category == fallback["category"]
            ).first()
            if fallback_module:
                recommended_module = fallback_module.id
                recommended_title = fallback_module.title

        return EducationalAnalysisResponse(
            analysis_text=analysis_text,
            recommended_module_id=recommended_module,
            recommended_module_title=recommended_title,
            detected_patterns=detected_pattern_names,
            urgency=urgency
        )
        
    except Exception as e:
        logger.error(f"Error in educational analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules", response_model=List[ModuleResponse])
async def get_all_modules(
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all available modules with optional filters
    If user_id provided, include their progress on each module
    """
    query = db.query(Module)
    
    if category:
        query = query.filter(Module.category == category)
    if difficulty:
        query = query.filter(Module.difficulty == difficulty)
    
    modules = query.all()
    
    response = []
    for module in modules:
        module_data = {
            "id": module.id,
            "title": module.title,
            "category": module.category,
            "difficulty": module.difficulty,
            "estimated_minutes": module.estimated_minutes,
            "exp_reward": module.exp_reward,
            "key_concepts": module.key_concepts or "",
            "progress": None
        }
        
        # Add user progress if user_id provided
        if user_id:
            progress = db.query(UserModuleProgress).filter(
                UserModuleProgress.user_id == user_id,
                UserModuleProgress.module_id == module.id
            ).first()
            
            if progress:
                module_data["progress"] = {
                    "status": progress.status,
                    "completion_percent": progress.completion_percent,
                    "quiz_score": progress.quiz_score,
                    "completed_at": progress.completed_at.isoformat() if progress.completed_at else None
                }
        
        response.append(ModuleResponse(**module_data))
    
    return response


@router.get("/modules/{module_id}")
async def get_module_detail(
    module_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get full module content including quiz questions"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Parse JSON content
    content = json.loads(module.content_json)
    quiz = json.loads(module.quiz_questions_json)
    
    # Get user progress if user_id provided
    progress = None
    if user_id:
        prog = db.query(UserModuleProgress).filter(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.module_id == module_id
        ).first()
        
        if prog:
            progress = {
                "status": prog.status,
                "completion_percent": prog.completion_percent,
                "quiz_score": prog.quiz_score,
                "quiz_attempts": prog.quiz_attempts,
                "last_accessed_at": prog.last_accessed_at.isoformat() if prog.last_accessed_at else None
            }
        
        # Update last accessed
        if prog:
            prog.last_accessed_at = datetime.utcnow()
            if prog.status == "not_started":
                prog.status = "in_progress"
            db.commit()
        else:
            # Create new progress record
            new_progress = UserModuleProgress(
                user_id=user_id,
                module_id=module_id,
                status="in_progress",
                last_accessed_at=datetime.utcnow()
            )
            db.add(new_progress)
            db.commit()
    
    return {
        "id": module.id,
        "title": module.title,
        "category": module.category,
        "difficulty": module.difficulty,
        "estimated_minutes": module.estimated_minutes,
        "exp_reward": module.exp_reward,
        "content": content,
        "quiz": quiz,
        "progress": progress
    }


@router.post("/quiz/submit", response_model=QuizSubmissionResponse)
async def submit_quiz(
    submission: QuizSubmissionRequest,
    db: Session = Depends(get_db)
):
    """Submit quiz answers and get results"""
    
    # Get module
    module = db.query(Module).filter(Module.id == submission.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Get quiz questions
    quiz_questions = json.loads(module.quiz_questions_json)
    
    # Grade quiz
    correct_count = 0
    explanations = []
    
    for i, (user_answer, question) in enumerate(zip(submission.answers, quiz_questions)):
        is_correct = user_answer == question['correct']
        if is_correct:
            correct_count += 1
        
        explanations.append({
            "question_number": i + 1,
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": question['correct'],
            "explanation": question['explanation']
        })
    
    # Calculate score
    score = int((correct_count / len(quiz_questions)) * 100)
    passed = correct_count == len(quiz_questions)  # Must get all correct
    
    # Award EXP if passed
    exp_earned = 0
    if passed:
        exp_earned = module.exp_reward
        
        # Update user stats
        user_stats = db.query(UserStats).filter(UserStats.user_id == submission.user_id).first()
        if user_stats:
            user_stats.total_exp += exp_earned
            user_stats.quiz_total_attempts += 1
            user_stats.quiz_correct_answers += correct_count
            
            # Update skill based on category
            category_skill_map = {
                "Technical_Analysis": "skill_technical_analysis",
                "Risk_Management": "skill_risk_management",
                "Psychology": "skill_psychology",
                "Market_Structure": "skill_market_structure"
            }
            
            skill_field = category_skill_map.get(module.category)
            if skill_field:
                current_skill = getattr(user_stats, skill_field, 0)
                # Increase skill by 10 points per module passed (capped at 100)
                setattr(user_stats, skill_field, min(current_skill + 10, 100))
            
            # Update streak if activity today
            today = date.today()
            if user_stats.last_activity_date != today:
                if user_stats.last_activity_date == today - timedelta(days=1):
                    user_stats.current_streak_days += 1
                else:
                    user_stats.current_streak_days = 1
                user_stats.last_activity_date = today
                
                if user_stats.current_streak_days > user_stats.longest_streak_days:
                    user_stats.longest_streak_days = user_stats.current_streak_days
        else:
            # Create user stats if not exists
            user_stats = UserStats(
                user_id=submission.user_id,
                total_exp=exp_earned,
                quiz_total_attempts=1,
                quiz_correct_answers=correct_count,
                current_streak_days=1,
                last_activity_date=date.today()
            )
            db.add(user_stats)
    
    # Update module progress
    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == submission.user_id,
        UserModuleProgress.module_id == submission.module_id
    ).first()
    
    if progress:
        progress.quiz_score = score
        progress.quiz_attempts += 1
        if passed:
            progress.status = "completed"
            progress.completion_percent = 100
            progress.completed_at = datetime.utcnow()
            
            # Increment completed count
            if user_stats:
                user_stats.modules_completed_count += 1
    
    db.commit()
    
    return QuizSubmissionResponse(
        score=score,
        correct_count=correct_count,
        total_questions=len(quiz_questions),
        exp_earned=exp_earned,
        passed=passed,
        explanations=explanations
    )


@router.get("/progress/{user_id}", response_model=ProgressResponse)
async def get_user_progress(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's overall educational progress"""
    
    # Get user stats
    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    if not stats:
        # Create default stats
        stats = UserStats(user_id=user_id)
        db.add(stats)
        db.commit()
    
    # Get total modules count
    total_modules = db.query(func.count(Module.id)).scalar()
    
    # Get category progress
    category_progress = {}
    for category in ["Technical_Analysis", "Risk_Management", "Psychology", "Market_Structure"]:
        category_total = db.query(func.count(Module.id)).filter(Module.category == category).scalar()
        category_completed = db.query(func.count(UserModuleProgress.id)).filter(
            UserModuleProgress.user_id == user_id,
            UserModuleProgress.status == "completed"
        ).join(Module).filter(Module.category == category).scalar()
        
        category_progress[category] = {
            "completed": category_completed,
            "total": category_total,
            "percentage": int((category_completed / category_total * 100)) if category_total > 0 else 0
        }
    
    return ProgressResponse(
        total_exp=stats.total_exp,
        current_level=stats.current_level,
        current_streak_days=stats.current_streak_days,
        skill_scores={
            "Technical_Analysis": stats.skill_technical_analysis,
            "Risk_Management": stats.skill_risk_management,
            "Psychology": stats.skill_psychology,
            "Market_Structure": stats.skill_market_structure
        },
        modules_completed=stats.modules_completed_count,
        total_modules=total_modules,
        category_progress=category_progress
    )


class GenerateCurriculumRequest(BaseModel):
    """Request to generate all quiz content for a user"""
    user_id: int


@router.post("/generate-curriculum")
async def generate_curriculum(
    request: GenerateCurriculumRequest,
    db: Session = Depends(get_db)
):
    """
    Generate and store all quiz questions for a user's curriculum.
    Called once when user clicks 'Start My Curriculum'.
    Module 1 (RSI) uses AI generation; modules 2-12 store hardcoded quizzes.
    Idempotent: skips modules that already have stored quizzes.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trader_type = user.trader_type or "momentum"
    generator = get_module_generator()

    generated_count = 0
    ai_generated_count = 0
    cached_count = 0

    for module_def in MODULES:
        mid = module_def["id"]

        # Check if quiz already exists for this module/trader/user
        existing = db.query(GeneratedQuiz).filter(
            GeneratedQuiz.module_id == mid,
            GeneratedQuiz.trader_type == trader_type,
            GeneratedQuiz.user_id == request.user_id,
        ).first()

        if existing:
            cached_count += 1
            continue

        if module_def.get("ai_generated_quiz"):
            # AI-generated quiz for module 1
            try:
                result = await generator.generate_module(
                    title=module_def["title"],
                    category=module_def["category"],
                    difficulty="beginner",
                    target_concepts=module_def["key_concepts"],
                    trader_type=trader_type,
                )
                quiz_json = result["quiz_questions_json"]
                ai_generated_count += 1
            except Exception as e:
                logger.error(f"AI generation failed for module {mid}: {e}")
                continue
        else:
            # Hardcoded quiz
            quiz_questions = generator.get_hardcoded_quiz(mid, trader_type)
            if not quiz_questions:
                continue
            quiz_json = json.dumps(quiz_questions)

        new_quiz = GeneratedQuiz(
            module_id=mid,
            trader_type=trader_type,
            user_id=request.user_id,
            quiz_questions_json=quiz_json,
            ai_generated=module_def.get("ai_generated_quiz", False),
        )
        db.add(new_quiz)
        generated_count += 1

    # Ensure UserStats exists
    stats = db.query(UserStats).filter(UserStats.user_id == request.user_id).first()
    if not stats:
        stats = UserStats(user_id=request.user_id)
        db.add(stats)

    db.commit()

    return {
        "generated": generated_count,
        "ai_generated": ai_generated_count,
        "cached": cached_count,
        "total_modules": len(MODULES),
    }


@router.get("/dashboard/{user_id}")
async def get_dashboard_data(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get personalized dashboard data based on user's trader type.
    Returns learning paths with modules and progress.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trader_type = user.trader_type or "momentum"
    generator = get_module_generator()
    modules = generator.get_all_modules(trader_type)

    # Get user stats
    stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    if not stats:
        stats = UserStats(user_id=user_id)
        db.add(stats)
        db.commit()
        db.refresh(stats)

    # Get user progress for all modules
    progress_records = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id
    ).all()
    progress_map = {p.module_id: p for p in progress_records}

    # Build learning paths (grouped by category)
    categories = {}
    for m in modules:
        cat = m["category"]
        if cat not in categories:
            categories[cat] = {"modules": [], "completed": 0, "total": 0}
        prog = progress_map.get(m["id"])
        module_data = {
            **m,
            "status": prog.status if prog else "not_started",
            "completion_percent": prog.completion_percent if prog else 0,
            "quiz_score": prog.quiz_score if prog else None,
        }
        categories[cat]["modules"].append(module_data)
        categories[cat]["total"] += 1
        if prog and prog.status == "completed":
            categories[cat]["completed"] += 1

    # Calculate category progress percentages
    learning_paths = []
    for cat, data in categories.items():
        pct = int((data["completed"] / data["total"] * 100)) if data["total"] > 0 else 0
        learning_paths.append({
            "category": cat,
            "progress_percent": pct,
            "completed": data["completed"],
            "total": data["total"],
            "modules": data["modules"],
        })

    return {
        "trader_type": trader_type,
        "user_name": user.name,
        "streak_days": stats.current_streak_days,
        "total_exp": stats.total_exp,
        "current_level": stats.current_level,
        "skill_scores": {
            "Technical_Analysis": stats.skill_technical_analysis,
            "Risk_Management": stats.skill_risk_management,
            "Psychology": stats.skill_psychology,
            "Market_Structure": stats.skill_market_structure,
        },
        "learning_paths": learning_paths,
    }


@router.get("/modules/{module_id}/quiz")
async def get_module_quiz(
    module_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get quiz questions for a module, personalized by trader type.
    Checks DB (GeneratedQuiz) first for pre-generated content.
    Falls back to AI generation or hardcoded questions if not in DB.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trader_type = user.trader_type or "momentum"
    generator = get_module_generator()

    module_def = next((m for m in MODULES if m["id"] == module_id), None)
    if not module_def:
        raise HTTPException(status_code=404, detail="Module not found")

    content = None

    # 1. Check DB for pre-generated quiz (from generate-curriculum)
    stored = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.module_id == module_id,
        GeneratedQuiz.trader_type == trader_type,
        GeneratedQuiz.user_id == user_id,
    ).first()

    if stored:
        quiz_questions = json.loads(stored.quiz_questions_json)
    elif module_def.get("ai_generated_quiz"):
        # 2. Fallback: AI-generate on the fly
        try:
            result = await generator.generate_module(
                title=module_def["title"],
                category=module_def["category"],
                difficulty="beginner",
                target_concepts=module_def["key_concepts"],
                trader_type=trader_type,
            )
            quiz_questions = json.loads(result["quiz_questions_json"])
            content = json.loads(result["content_json"])
        except Exception as e:
            logger.error(f"AI generation failed for module {module_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")
    else:
        # 3. Fallback: hardcoded quiz
        quiz_questions = generator.get_hardcoded_quiz(module_id, trader_type)
        if not quiz_questions:
            raise HTTPException(status_code=404, detail="Quiz not found for this module")

    # Update/create progress record
    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.module_id == module_id
    ).first()
    if not progress:
        progress = UserModuleProgress(
            user_id=user_id,
            module_id=module_id,
            status="in_progress",
            last_accessed_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.last_accessed_at = datetime.utcnow()
        if progress.status == "not_started":
            progress.status = "in_progress"
    db.commit()

    return {
        "module_id": module_id,
        "title": module_def["title"],
        "category": module_def["category"],
        "trader_type": trader_type,
        "focus": module_def.get(f"{trader_type}_focus", ""),
        "quiz_questions": quiz_questions,
        "content": content,
        "ai_generated": module_def.get("ai_generated_quiz", False),
    }


@router.post("/quiz/submit-v2")
async def submit_quiz_v2(
    submission: QuizSubmissionRequest,
    db: Session = Depends(get_db)
):
    """
    Submit quiz answers (works with the new module system).
    Grades against hardcoded or AI-generated quiz questions.
    """
    user = db.query(User).filter(User.id == submission.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    trader_type = user.trader_type or "momentum"
    generator = get_module_generator()

    module_def = next((m for m in MODULES if m["id"] == submission.module_id), None)
    if not module_def:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get quiz questions to grade against — check DB first, then hardcoded
    stored = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.module_id == submission.module_id,
        GeneratedQuiz.trader_type == trader_type,
        GeneratedQuiz.user_id == submission.user_id,
    ).first()

    if stored:
        quiz_questions = json.loads(stored.quiz_questions_json)
    else:
        quiz_questions = generator.get_hardcoded_quiz(submission.module_id, trader_type)

    if not quiz_questions:
        raise HTTPException(status_code=400, detail="Cannot grade: quiz questions not available. Generate curriculum first.")

    # Grade
    correct_count = 0
    explanations = []
    for i, (user_answer, question) in enumerate(zip(submission.answers, quiz_questions)):
        is_correct = user_answer.upper() == question["correct"].upper()
        if is_correct:
            correct_count += 1
        explanations.append({
            "question_number": i + 1,
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": question["correct"],
            "explanation": question["explanation"],
        })

    total = len(quiz_questions)
    score = int((correct_count / total) * 100) if total > 0 else 0
    passed = correct_count == total

    # Get or create user stats (always, not just on pass)
    stats = db.query(UserStats).filter(UserStats.user_id == submission.user_id).first()
    if not stats:
        stats = UserStats(user_id=submission.user_id, total_exp=0)
        db.add(stats)

    # Per-answer XP (always awarded): +20 correct, +5 incorrect
    answer_xp = (correct_count * 20) + ((total - correct_count) * 5)
    stats.total_exp += answer_xp
    stats.quiz_total_attempts += 1
    stats.quiz_correct_answers += correct_count

    exp_earned = answer_xp

    # Check if module was already completed (to avoid double-counting)
    progress = db.query(UserModuleProgress).filter(
        UserModuleProgress.user_id == submission.user_id,
        UserModuleProgress.module_id == submission.module_id
    ).first()
    already_completed = progress and progress.status == "completed"

    if passed and not already_completed:
        # Module completion bonus (only first time)
        module_bonus = module_def["exp_reward"]
        stats.total_exp += module_bonus
        exp_earned += module_bonus

        # Update skill
        category_skill_map = {
            "Technical_Analysis": "skill_technical_analysis",
            "Risk_Management": "skill_risk_management",
            "Psychology": "skill_psychology",
            "Advanced_Strategies": "skill_market_structure",
        }
        skill_field = category_skill_map.get(module_def["category"])
        if skill_field:
            current = getattr(stats, skill_field, 0)
            setattr(stats, skill_field, min(current + 10, 100))

        stats.modules_completed_count += 1

    # Update streak
    today = date.today()
    if stats.last_activity_date != today:
        if stats.last_activity_date == today - timedelta(days=1):
            stats.current_streak_days += 1
        else:
            stats.current_streak_days = 1
        stats.last_activity_date = today
        if stats.current_streak_days > stats.longest_streak_days:
            stats.longest_streak_days = stats.current_streak_days

    # Calculate level
    stats.current_level = (stats.total_exp // 200) + 1

    # Update module progress (reuse progress queried above)
    if not progress:
        progress = UserModuleProgress(
            user_id=submission.user_id,
            module_id=submission.module_id,
            status="completed" if passed else "in_progress",
            quiz_score=score,
            quiz_attempts=1,
            completion_percent=100 if passed else 50,
            completed_at=datetime.utcnow() if passed else None,
        )
        db.add(progress)
    else:
        progress.quiz_score = score
        progress.quiz_attempts += 1
        if passed:
            progress.status = "completed"
            progress.completion_percent = 100
            progress.completed_at = datetime.utcnow()

    db.commit()

    return {
        "score": score,
        "correct_count": correct_count,
        "total_questions": total,
        "exp_earned": exp_earned,
        "total_exp": stats.total_exp,
        "current_level": stats.current_level,
        "passed": passed,
        "explanations": explanations,
    }


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get leaderboard of top learners"""
    
    top_users = db.query(
        UserStats.user_id,
        UserStats.total_exp,
        UserStats.current_streak_days,
        UserStats.modules_completed_count,
        User.name
    ).join(User, User.id == UserStats.user_id).order_by(
        UserStats.total_exp.desc()
    ).limit(limit).all()
    
    leaderboard = []
    for rank, (user_id, exp, streak, modules, name) in enumerate(top_users, 1):
        leaderboard.append({
            "rank": rank,
            "name": name,
            "exp": exp,
            "streak_days": streak,
            "modules_completed": modules
        })
    
    return {"leaderboard": leaderboard}
