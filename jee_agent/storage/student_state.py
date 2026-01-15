from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, date
from enum import Enum

class Confidence(str, Enum):
    ZERO = "zero"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MASTERED = "mastered"

class TopicProgress(BaseModel):
    topic_name: str
    subject: str
    confidence: Confidence = Confidence.ZERO
    pyqs_attempted: int = 0
    pyqs_correct: int = 0
    accuracy: float = 0.0
    time_spent_mins: int = 0
    last_practiced: Optional[datetime] = None
    weak_subtopics: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

class LectureProgress(BaseModel):
    lecture_id: str
    title: str
    completed: bool = False
    watch_time_mins: int = 0
    recommended_speed: float = 1.0
    key_timestamps: List[int] = Field(default_factory=list)
    post_quiz_score: Optional[float] = None

class SessionLog(BaseModel):
    session_id: str
    date: date
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_mins: int = 0
    topics_covered: List[str] = Field(default_factory=list)
    pyqs_solved: int = 0
    accuracy: float = 0.0
    mood: str = "neutral"
    breakthroughs: List[str] = Field(default_factory=list)
    struggles: List[str] = Field(default_factory=list)

class DailyPlan(BaseModel):
    day_number: int
    date: date
    focus_subject: str
    target_topics: List[str]
    target_pyqs: int
    lectures_to_watch: List[str]
    estimated_hours: float
    completed: bool = False
    actual_performance: Optional[Dict] = None

class StudentState(BaseModel):
    """Complete student state - persisted across all sessions"""
    
    # Identity
    student_id: str
    name: str = "Student"
    exam_date: date
    daily_hours_available: List[float] = Field(default_factory=lambda: [10.0] * 8)
    energy_peak_time: str = "morning"
    
    # Knowledge Map
    physics_topics: Dict[str, TopicProgress] = Field(default_factory=dict)
    chemistry_topics: Dict[str, TopicProgress] = Field(default_factory=dict)
    math_topics: Dict[str, TopicProgress] = Field(default_factory=dict)
    
    # Lecture Progress
    lectures: Dict[str, LectureProgress] = Field(default_factory=dict)
    
    # Session History
    sessions: List[SessionLog] = Field(default_factory=list)
    current_session: Optional[SessionLog] = None
    
    # Adaptive Plan
    daily_plans: List[DailyPlan] = Field(default_factory=list)
    
    # Behavioral Patterns (learned over time)
    avg_accuracy_by_subject: Dict[str, float] = Field(default_factory=dict)
    effective_interventions: List[str] = Field(default_factory=list)
    stress_triggers: List[str] = Field(default_factory=list)
    preferred_session_length_mins: int = 120
    
    def get_topic_progress(self, subject: str, topic: str) -> Optional[TopicProgress]:
        topic_map = getattr(self, f"{subject}_topics", {})
        return topic_map.get(topic)
    
    def update_topic_progress(self, subject: str, topic: str, progress: TopicProgress):
        topic_map = getattr(self, f"{subject}_topics", {})
        topic_map[topic] = progress
        setattr(self, f"{subject}_topics", topic_map)
    
    def get_weakest_topics(self, n: int = 5) -> List[TopicProgress]:
        all_topics = []
        for subject in ["physics", "chemistry", "math"]:
            topic_map = getattr(self, f"{subject}_topics", {})
            all_topics.extend(topic_map.values())
        return sorted(all_topics, key=lambda x: x.accuracy)[:n]
    
    def get_overall_accuracy(self) -> float:
        total_attempted = 0
        total_correct = 0
        for subject in ["physics", "chemistry", "math"]:
            topic_map = getattr(self, f"{subject}_topics", {})
            for progress in topic_map.values():
                total_attempted += progress.pyqs_attempted
                total_correct += progress.pyqs_correct
        return total_correct / max(total_attempted, 1)
    
    def days_remaining(self) -> int:
        return (self.exam_date - date.today()).days