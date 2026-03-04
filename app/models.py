import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("SurveyQuestion", back_populates="survey")


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id"))
    question_text = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

    survey = relationship("Survey", back_populates="questions")


class SurveySubmission(Base):
    __tablename__ = "survey_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id"))

    ip_address = Column(String)
    device = Column(String)
    browser = Column(String)
    os = Column(String)
    location = Column(String)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    overall_score = Column(Float)

    answers = relationship("SurveyAnswer", back_populates="submission",cascade="all, delete")
    media_files = relationship("MediaFile",back_populates="submission",cascade="all, delete")

from sqlalchemy import Column, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime


class SurveyAnswer(Base):
    __tablename__ = "survey_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("survey_submissions.id"))
    question_id = Column(UUID(as_uuid=True), ForeignKey("survey_questions.id"))

    answer = Column(String)
    face_detected = Column(Boolean)
    face_score = Column(Float)
    face_image_path = Column(String)

    submission = relationship("SurveySubmission", back_populates="answers")


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("survey_submissions.id"))
    type = Column(String)
    path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship(
        "SurveySubmission",
        back_populates="media_files"
    )