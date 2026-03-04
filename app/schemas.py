from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime


#SURVEY SCHEMAS

class SurveyCreate(BaseModel):
    title: str


class QuestionCreate(BaseModel):
    question_text: str
    order: int


class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    order: int

    class Config:
        from_attributes = True


class SurveyResponse(BaseModel):
    id: UUID
    title: str
    is_active: bool
    created_at: datetime
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True


#SUBMISSION SCHEMAS


class SubmissionStartResponse(BaseModel):
    id: UUID
    survey_id: UUID
    started_at: datetime

    class Config:
        from_attributes = True


class AnswerCreate(BaseModel):
    question_id: UUID
    answer: str
    face_detected: bool
    face_score: float
    face_image_path: str



class CompleteResponse(BaseModel):
    message: str
    overall_score: float