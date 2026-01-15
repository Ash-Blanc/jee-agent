from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from agno.knowledge.json import JSONKnowledgeBase
from agno.knowledge.embedder.mistral import MistralEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from jee_agent.config.settings import VECTOR_DB_PATH, EMBEDDING_MODEL

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class PYQ(BaseModel):
    id: str
    question_text: str
    options: List[str]
    correct_answer: str
    year: int
    subject: str
    topic: str
    subtopic: str
    difficulty: Difficulty
    frequency_score: float  # How often this pattern appears
    common_mistakes: List[str]
    solution_approach: str
    time_expected_secs: int
    tags: List[str] = []

class PYQKnowledge:
    """Manages the PYQ knowledge base with vector search"""
    
    def __init__(self):
        self.vector_db = LanceDb(
            uri=VECTOR_DB_PATH,
            table_name="jee_pyqs",
            search_type=SearchType.hybrid,
            embedder=MistralEmbedder(id=EMBEDDING_MODEL)
        )
        self.knowledge_base = JSONKnowledgeBase(
            path="data/pyqs/",
            vector_db=self.vector_db
        )
    
    def search_pyqs(
        self, 
        topic: str, 
        difficulty: Optional[Difficulty] = None,
        limit: int = 5
    ) -> List[PYQ]:
        query = f"JEE Main {topic} questions"
        if difficulty:
            query += f" {difficulty.value} level"
        
        results = self.knowledge_base.search(query, limit=limit)
        return [PYQ(**r.metadata) for r in results if r.metadata]
    
    def get_high_frequency_pyqs(self, subject: str, limit: int = 10) -> List[PYQ]:
        query = f"Most frequently asked {subject} JEE patterns"
        results = self.knowledge_base.search(query, limit=limit)
        pyqs = [PYQ(**r.metadata) for r in results if r.metadata]
        return sorted(pyqs, key=lambda x: x.frequency_score, reverse=True)
    
    def get_progressive_set(self, topic: str, count: int = 5) -> List[PYQ]:
        """Returns PYQs in easy -> medium -> hard progression"""
        easy = self.search_pyqs(topic, Difficulty.EASY, limit=2)
        medium = self.search_pyqs(topic, Difficulty.MEDIUM, limit=2)
        hard = self.search_pyqs(topic, Difficulty.HARD, limit=1)
        return (easy + medium + hard)[:count]