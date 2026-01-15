from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.json_reader import JSONReader
from agno.knowledge.embedder.mistral import MistralEmbedder
from agno.vectordb.pgvector import PgVector, SearchType
from jee_agent.config.settings import DATABASE_URL, EMBEDDING_MODEL, MISTRAL_API_KEY


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
    """Manages the PYQ knowledge base with PostgreSQL vector search (PgVector)"""
    
    def __init__(self):
        self.vector_db = PgVector(
            db_url=DATABASE_URL,
            table_name="jee_pyqs",
            search_type=SearchType.hybrid,
            embedder=MistralEmbedder(id=EMBEDDING_MODEL, api_key=MISTRAL_API_KEY)
        )
        # Initialize generic Knowledge base
        self.knowledge_base = Knowledge(
            vector_db=self.vector_db,
            # We don't load on init to avoid overhead/duplication, 
            # assume data is loaded or will be loaded via a separate script/method
        )
    
    def load_data(self, path: str = "jee_agent/data/pyqs/"):
        """Loads data from JSON files into the vector database"""
        self.knowledge_base.load(path=path, reader=JSONReader())

    def search_pyqs(
        self, 
        topic: str, 
        difficulty: Optional[Difficulty] = None,
        limit: int = 5
    ) -> List[PYQ]:
        query = f"JEE Main {topic} questions"
        if difficulty:
            query += f" {difficulty.value} level"
        
        try:
            # Knowledge.search returns list of Document objects
            results = self.knowledge_base.search(query, limit=limit)
        except Exception as e:
            # Return empty list on embedding/search failure to prevent crash
            print(f"Error searching PYQs: {e}")
            return []
        
        # Convert Document metadata back to PYQ objects
        pyqs = []
        for r in results:
            if r.meta:
                 # Ensure strict validation or handle potential missing fields
                 try:
                     pyqs.append(PYQ(**r.meta))
                 except Exception:
                     continue
        return pyqs
    
    def get_high_frequency_pyqs(self, subject: str, limit: int = 10) -> List[PYQ]:
        query = f"Most frequently asked {subject} JEE patterns"
        try:
            results = self.knowledge_base.search(query, limit=limit)
        except Exception as e:
            print(f"Error getting high freq PYQs: {e}")
            return []
            
        pyqs = []
        for r in results:
            if r.meta:
                 try:
                     pyqs.append(PYQ(**r.meta))
                 except Exception:
                     continue
        return sorted(pyqs, key=lambda x: x.frequency_score, reverse=True)
    
    def get_progressive_set(self, topic: str, count: int = 5) -> List[PYQ]:
        """Returns PYQs in easy -> medium -> hard progression"""
        try:
            easy = self.search_pyqs(topic, Difficulty.EASY, limit=2)
            medium = self.search_pyqs(topic, Difficulty.MEDIUM, limit=2)
            hard = self.search_pyqs(topic, Difficulty.HARD, limit=1)
            return (easy + medium + hard)[:count]
        except Exception:
            return []
