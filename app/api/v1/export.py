import io
import logging
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from app.schemas.responses import ExportResponse
from app.services.export_service import ExportService
from app.api.v1.generate import job_store

router = APIRouter(tags=["Export"])
logger = logging.getLogger(__name__)

@router.get("/export/{job_id}", response_model=ExportResponse)
async def export_job(
    job_id: str,
    format: str = Query("json", description="Export format: json or csv"),
    download: bool = Query(False, description="Return as a file download")
):
    """
    Export generated variations for a specific job.
    """
    if job_id not in job_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    response = job_store[job_id]
    export_service = ExportService()
    
    fmt = format.lower()
    if fmt not in ["json", "csv"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format. Must be 'json' or 'csv'.")

    try:
        if fmt == "csv":
            content = export_service.to_csv(response)
            filename = f"export_{job_id}.csv"
            media_type = "text/csv"
        else:
            content = export_service.to_json(response)
            filename = f"export_{job_id}.json"
            media_type = "application/json"
            
        if download:
            stream = io.StringIO(content)
            return StreamingResponse(
                iter([stream.getvalue()]), 
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        return ExportResponse(
            job_id=job_id,
            format=fmt,
            content=content,
            filename=filename
        )
    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Export failed")
