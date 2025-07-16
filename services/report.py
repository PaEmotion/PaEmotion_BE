from sqlalchemy.orm import Session
from models.report import UserReport
from schemas.report import ReportTypeEnum
from datetime import date
from typing import Optional, List

class ReportService:
    # 리포트 저장 함수
    @staticmethod
    def report_create(db: Session, user_id: int, report_date: date, 
                      report_type: ReportTypeEnum, report_text: str) -> UserReport:
        existing = db.query(UserReport).filter_by(
            userId=user_id,
            reportDate=report_date,
            reportType=report_type
        ).first()

        if existing:
            raise ValueError("해당 리포트가 이미 존재합니다.")

        report = UserReport(
            userId=user_id,
            reportDate=report_date,
            reportType=report_type,
            reportText=report_text
        )
        db.add(report)
        db.commit()
        db.refresh(report) 
        return report

    # 리포트 단건 조회 함수 (리포트 아이디로)
    @staticmethod
    def report_read(db: Session, report_id: int) -> UserReport:
        report = db.query(UserReport).filter_by(reportId=report_id).first()
        if not report:
            raise ValueError("리포트를 찾을 수 없습니다.")
        return report
    
    # 리포트 리스트 조회 함수 (유저, 기간 또는 날짜별로)
    @staticmethod
    def report_readbylist(
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        report_date: Optional[date] = None
    ) -> List[UserReport]:
        query = db.query(UserReport).filter(UserReport.userId == user_id)

        if report_date:
            query = query.filter(UserReport.reportDate == report_date)
        elif start_date and end_date:
            query = query.filter(UserReport.reportDate.between(start_date, end_date))

        return query.order_by(UserReport.reportDate.desc()).all()