from sqlalchemy.orm import Session
from ..db import models
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from fastapi.responses import StreamingResponse


def list_reports(db: Session, user_id: int):
    return db.query(models.Report).filter(models.Report.generated_by_user_id == user_id).all()


def get_report(db: Session, report_id: int):
    return db.query(models.Report).filter(models.Report.id == report_id).first()


def generate_report(db: Session, prediction: models.Prediction):
    """
    Generate AI clinical report in memory for download (no local file creation)
    """

    title = f"CKD Clinical Report - Stage {prediction.ckd_stage}"

    summary = (
        f"The patient is classified under CKD Stage {prediction.ckd_stage} "
        f"with a predicted eGFR of {prediction.egfr_predicted:.2f} mL/min/1.73m²."
    )

    detailed_analysis = (
        f"Model confidence: {prediction.egfr_confidence:.2f}\n"
        f"Stage confidence: {prediction.stage_confidence:.2f}\n"
        f"Risk level: {prediction.risk_level}\n\n"
        f"Top contributing features:\n"
    )

    for feature in prediction.top_contributing_features:
        detailed_analysis += f"- {feature['feature']}: {feature['importance']:.4f}\n"

    recommendations = "\n".join(prediction.recommendations)

    # 🔥 Generate PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(title, styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(summary, styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Clinical Analysis:", styles["Heading2"]))
    elements.append(Paragraph(detailed_analysis.replace("\n", "<br/>"), styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Recommendations:", styles["Heading2"]))
    elements.append(Paragraph(recommendations.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    # 🔥 Optional: still save report metadata in DB without pdf_path
    report = models.Report(
        prediction_id=prediction.id,
        generated_by_user_id=prediction.patient.user_id,
        title=title,
        summary=summary,
        detailed_analysis=detailed_analysis,
        recommendations=recommendations,
        pdf_path=None,  # No file path saved
        created_at=datetime.utcnow()
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    # 🔥 Return a StreamingResponse for direct download
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ckd_report_{prediction.id}.pdf"}
    )