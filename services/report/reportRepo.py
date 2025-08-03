from sqlalchemy.orm import Session
from models.report import UserReport
from schemas.reportRepo import ReportTypeEnum
from datetime import date
from typing import Optional, List

class ReportService:

    @staticmethod
    def get_existing_report(
        db: Session,
        userId: int,
        reportDate: date,
        reportType: ReportTypeEnum
        ) -> Optional[UserReport]:
        return db.query(UserReport).filter(
            UserReport.userId==userId,
            UserReport.reportDate==reportDate,
            UserReport.reportType==reportType
        ).first()

    @staticmethod
    def save_report(
        db: Session, 
        userId: int, 
        reportDate: date, 
        reportType: ReportTypeEnum, 
        reportText: str, 
        spendType: Optional[str] = None
        ) -> UserReport:

        report = UserReport(
            userId=userId,
            reportDate=reportDate,
            reportType=reportType,
            reportText=reportText,
            spendType=spendType
        )
        db.add(report)
        db.commit()
        db.refresh(report) 
        return report

    # 단건 (리포트 아이디로)
    @staticmethod
    def read_report(db: Session, report_id: int) -> UserReport:
        report = db.query(UserReport).filter_by(reportId=report_id).first()
        if not report:
            raise ValueError("리포트를 찾을 수 없습니다.")
        return report
    
        
    # 리스트 (유저, 기간 또는 날짜별로)
    @staticmethod
    def readbylist_reports(db: Session, user_id: Optional[int] = None, report_date: Optional[date] = None,
                          start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[UserReport]:
        query = db.query(UserReport)

        if user_id:
            query = query.filter(UserReport.userId == user_id)
        if report_date:
            query = query.filter(UserReport.reportDate == report_date)
        elif start_date and end_date:
            query = query.filter(UserReport.reportDate.between(start_date, end_date))

        reports = query.order_by(UserReport.reportDate.desc()).all()

            # spendType이 None이면 빈 문자열로 변경
        for report in reports:
            if report.spendType is None:
                report.spendType = ""

        return reports