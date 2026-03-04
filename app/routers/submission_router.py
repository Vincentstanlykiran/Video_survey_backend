from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from user_agents import parse
import os
import json
import zipfile
from .. import models, schemas
from ..dependencies import get_db
import geoip2.database
from uuid import uuid4

router = APIRouter(prefix="/submissions", tags=["Submissions"])





GEOIP_DB_PATH = os.getenv("GEOIP_DB_PATH", "geoip/GeoLite2-City.mmdb")

@router.post("/start/{survey_id}", response_model=schemas.SubmissionStartResponse)
def start_submission(
    survey_id: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    survey = db.query(models.Survey).filter(
        models.Survey.id == survey_id,
        models.Survey.is_active == True
    ).first()

    if not survey:
        raise HTTPException(status_code=404, detail="Active survey not found")

    ip_address = request.client.host
    user_agent_string = request.headers.get("user-agent")
    user_agent = parse(user_agent_string)

    device = "Mobile" if user_agent.is_mobile else "Desktop"
    browser = user_agent.browser.family
    os_name = user_agent.os.family

   
    location = "Unknown"
    try:
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.city(ip_address)
            city = response.city.name
            country = response.country.name
            location = f"{city}, {country}" if city else country
    except Exception as e:
        print(f"GeoIP lookup failed: {e}")

    submission = models.SurveySubmission(
        survey_id=survey_id,
        ip_address=ip_address,
        device=device,
        browser=browser,
        os=os_name,
        location=location,
        started_at=datetime.utcnow()
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission



@router.post("/{submission_id}/answers")
def create_answer(
    submission_id: UUID,
    answer: schemas.AnswerCreate,
    db: Session = Depends(get_db)
):
    submission = db.query(models.SurveySubmission).filter(
        models.SurveySubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    new_answer = models.SurveyAnswer(
        submission_id=submission_id,
        question_id=answer.question_id,
        answer=answer.answer,
        face_detected=answer.face_detected,
        face_score=answer.face_score,
        face_image_path=answer.face_image_path,
    )

    db.add(new_answer)
    db.commit()

    return {"message": "Answer saved"}




@router.post("/{submission_id}/complete", response_model=schemas.CompleteResponse)
def complete_submission(
    submission_id: UUID,
    db: Session = Depends(get_db)
):
    submission = db.query(models.SurveySubmission).filter(
        models.SurveySubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    answers = db.query(models.SurveyAnswer).filter(
        models.SurveyAnswer.submission_id == submission_id
    ).all()

    if len(answers) != 5:
        raise HTTPException(
            status_code=400,
            detail="All 5 questions must be answered"
        )

    total_score = sum(a.face_score for a in answers)
    overall_score = total_score / len(answers)

    submission.completed_at = datetime.utcnow()
    submission.overall_score = overall_score

    db.commit()

    return {
        "message": "Submission completed successfully",
        "overall_score": overall_score
    }




@router.post("/{submission_id}/media")
def upload_media(
    submission_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    submission = db.query(models.SurveySubmission).filter(
        models.SurveySubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

  
    if file.content_type.startswith("image"):
        folder = "media/images"
        media_type = "image"
    elif file.content_type.startswith("video"):
        folder = "media/videos"
        media_type = "video"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    os.makedirs(folder, exist_ok=True)

  
   
    extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid4()}{extension}"
    file_location = os.path.join(folder, filename)

   
    with open(file_location, "wb") as buffer:
        buffer.write(file.file.read())

    media_record = models.MediaFile(
        submission_id=submission_id,
        type=media_type,
        path=file_location
    )

    db.add(media_record)
    db.commit()

    return {
        "message": "File uploaded successfully",
        "file_path": file_location
    }


@router.get("/{submission_id}/export")
def export_submission(
    submission_id: UUID,
    db: Session = Depends(get_db)
):
    submission = db.query(models.SurveySubmission).filter(
        models.SurveySubmission.id == submission_id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    answers = db.query(models.SurveyAnswer).filter(
        models.SurveyAnswer.submission_id == submission_id
    ).all()

    media_files = db.query(models.MediaFile).filter(
        models.MediaFile.submission_id == submission_id
    ).all()

    metadata = {
        "submission_id": str(submission.id),
        "survey_id": str(submission.survey_id),
        "started_at": submission.started_at.isoformat() if submission.started_at else None,
        "completed_at": submission.completed_at.isoformat() if submission.completed_at else None,
        "ip_address": submission.ip_address,
        "device": submission.device,
        "browser": submission.browser,
        "os": submission.os,
        "location": submission.location,
        "responses": [],
        "overall_score": submission.overall_score
    }

    for answer in answers:
        metadata["responses"].append({
            "question_id": str(answer.question_id),
            "answer": answer.answer,
            "face_detected": answer.face_detected,
            "score": answer.face_score,
            "face_image": answer.face_image_path
        })

    export_folder = f"media/exports/{submission_id}"
    os.makedirs(export_folder, exist_ok=True)

    metadata_path = f"{export_folder}/metadata.json"

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    zip_path = f"{export_folder}/submission_{submission_id}.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(metadata_path, arcname="metadata.json")

        for media in media_files:
            if os.path.exists(media.path):
                if media.type == "video":
                    arcname = f"videos/{os.path.basename(media.path)}"
                else:
                    arcname = f"images/{os.path.basename(media.path)}"

                zipf.write(media.path, arcname=arcname)

    return FileResponse(
        path=zip_path,
        filename=f"submission_{submission_id}.zip",
        media_type="application/zip"
    )