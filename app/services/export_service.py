import csv
from io import StringIO
from app.schemas.responses import GenerateResponse

class ExportService:
    """Service for exporting variations to different formats."""
    
    @staticmethod
    def to_json(response: GenerateResponse) -> str:
        """Export the generation response to a JSON string."""
        return response.model_dump_json(indent=2)
        
    @staticmethod
    def to_csv(response: GenerateResponse) -> str:
        """Export the generated variations to a CSV string."""
        output = StringIO()
        
        if not response.variations:
            return output.getvalue()
            
        fieldnames = [
            'id', 'question', 'answer_key', 'difficulty', 
            'question_type', 'topic', 'subtopic', 
            'confidence_score', 'flagged_for_review'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for variation in response.variations:
            row_dict = variation.model_dump()
            writer.writerow(row_dict)
            
        return output.getvalue()
        
    @staticmethod
    def get_filename(job_id: str, format: str) -> str:
        """Generate a standard filename for exports."""
        return f"variations_{job_id}.{format}"
