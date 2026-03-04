from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from app.db import models
from app.api.deps import get_db_session, get_patient_user
from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("")
def list_reports(
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    reports = report_service.list_reports(db, current_user.id)

    if not reports:
        return {
            "message": "No reports generated yet.",
            "reports": []
        }

    return {
        "message": "Reports fetched successfully.",
        "reports": reports
    }

@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    current_user: models.User = Depends(get_patient_user),
    db: Session = Depends(get_db_session),
):
    report = report_service.get_report(db, report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.prediction.patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Generate PDF in-memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(report.title, styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(report.summary, styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Clinical Analysis:", styles["Heading2"]))
    elements.append(Paragraph(report.detailed_analysis.replace("\n", "<br/>"), styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Recommendations:", styles["Heading2"]))
    elements.append(Paragraph(report.recommendations.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ckd_report_{report.id}.pdf"}
    )