from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from .. import models, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/surveys", tags=["Surveys"])


@router.post("", response_model=schemas.SurveyResponse)
def create_survey(payload: schemas.SurveyCreate, db: Session = Depends(get_db)):
    survey = models.Survey(title=payload.title)
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


@router.post("/{survey_id}/questions", response_model=schemas.QuestionResponse)
def add_question(survey_id: UUID, payload: schemas.QuestionCreate, db: Session = Depends(get_db)):
    survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    question_count = db.query(models.SurveyQuestion)\
        .filter(models.SurveyQuestion.survey_id == survey_id)\
        .count()

    if question_count >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 questions allowed")

    question = models.SurveyQuestion(
        survey_id=survey_id,
        question_text=payload.question_text,
        order=payload.order
    )

    db.add(question)
    db.commit()
    db.refresh(question)
    return question



@router.get("/{survey_id}", response_model=schemas.SurveyResponse)
def get_survey(survey_id: UUID, db: Session = Depends(get_db)):
    survey = db.query(models.Survey)\
        .filter(models.Survey.id == survey_id)\
        .first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    survey.questions.sort(key=lambda x: x.order)
    return survey



@router.post("/{survey_id}/publish")
def publish_survey(survey_id: UUID, db: Session = Depends(get_db)):
    survey = db.query(models.Survey)\
        .filter(models.Survey.id == survey_id)\
        .first()

    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    question_count = db.query(models.SurveyQuestion)\
        .filter(models.SurveyQuestion.survey_id == survey_id)\
        .count()

    if question_count != 5:
        raise HTTPException(status_code=400, detail="Survey must have exactly 5 questions to publish")

    survey.is_active = True
    db.commit()

    return {"message": "Survey published successfully"}