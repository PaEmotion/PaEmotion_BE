from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.reportGPT import ReportRequest
from services.report.reportGPT import generate_report
from services.report.data import get_gpt_data, format_report_data
from services.report.reportRepo import ReportService
from services.ml.type import classify_type
from services.ml.budget import training_and_prediction

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
    consumption_type = None # 기본값

    # 2. records -> 문자열 데이터로 포맷하기
    if not gpt_data:
        return {"success": False, "message": "해당 기간에 소비 기록이 없습니다."}

    if gpt_data['total_spend'] <= 0 or sum(gpt_data['emotion_count'].values()) == 0:
        return {"success": False, "message": "소비 기록이 부족하여 리포트를 생성할 수 없습니다."}

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
        budget_prediction = (
            int(budget_prediction[0]) if budget_prediction else None
        )

    existing_report = ReportService.get_existing_report(db, userId, request.reportDate, request.period)
    if existing_report:
        return {"report": existing_report.reportText}
    
    # 3. GPT 호출
    report = generate_report(request.period, data_str, request.tone, spend_type=consumption_type or "", budget_prediction=budget_prediction)

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

    return {"report": report}
