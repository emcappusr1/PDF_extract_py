from pydantic import BaseModel
from typing import List

class QuestionData(BaseModel):
    """Model for a single MCQ question"""
    content: str
    optionA: str
    optionB: str
    optionC: str
    optionD: str
    correctAnswer: str

class ExtractResponse(BaseModel):
    """Response model for PDF extraction"""
    questions: List[QuestionData]
    total_questions: int

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
