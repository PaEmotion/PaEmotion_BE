from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.reportGPT import ReportRequest
from services.report.reportGPT import generate_report
from services.report.data import get_gpt_data, format_report_data
from services.report.reportRepo import ReportService
from services.ml.type import classify_type
from services.ml.budget import training_and_prediction
from utils.response import response_success, response_error
import numpy as np

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/create")
async def create_report(
    userId: int,
    request: ReportRequest,
    db: Session = Depends(get_db),
):

    # 1. 소비 데이터 가져오기
    gpt_data = await get_gpt_data(userId, request, db)

    budget_prediction = None # 기본값
    budget_prediction_real = None 
    consumption_type = None

    # 2. records -> 문자열 데이터로 포맷하기
    if not gpt_data:
        return response_error(message="해당 기간에 소비 기록이 없습니다.", status_code=404)

    if gpt_data['total_spend'] <= 0 or sum(gpt_data['emotion_count'].values()) == 0:
        return response_error(message="소비 기록이 부족하여 리포트를 생성할 수 없습니다.", status_code=400)

    if request.period == "monthly":
        data_str = format_report_data(
            gpt_data['total_spend'],
            gpt_data['emotion_count'],
            gpt_data['spend_to_emotion'],
            gpt_data['most_emotion'],
            gpt_data.get('category_ranking') 
        )

        consumption_type = classify_type(
            db=db,
            userId=userId,
            year=request.reportDate.year,
            month=request.reportDate.month
        )

    else:
        data_str = format_report_data(
            gpt_data['total_spend'],
            gpt_data['emotion_count'],
            gpt_data['spend_to_emotion'],
            gpt_data['most_emotion']
        )

        budget_prediction = training_and_prediction(db, userId)
        budget_prediction_real = np.exp(budget_prediction)
        try:
            budget_prediction_real = int(budget_prediction_real[0])
        except (TypeError, IndexError):
            budget_prediction_real = int(budget_prediction_real) if budget_prediction_real is not None else None

    existing_report = ReportService.get_existing_report(db, userId, request.reportDate, request.period)
    if existing_report:
        return response_success(
            data = {"report": existing_report.reportText},
            message = "이미 존재하는 리포트 입니다."
        )
    
    # 3. GPT 호출
    report = generate_report(request.period, data_str, request.tone, spend_type=consumption_type or "", budget_prediction=budget_prediction_real)

    try:
        saved_report = ReportService.save_report(
            db=db,
            userId=userId,
            reportDate=request.reportDate,  
            reportType=request.period,  
            reportText=report,
            spendType=consumption_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response_success(data={"report": report}, message="리포트 생성 성공")
