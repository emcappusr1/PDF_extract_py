from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path

# Import custom modules
from models import ExtractResponse, ErrorResponse
from pdf_parser import PDFParser
from question_extractor import QuestionExtractor

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(
    title="MCQ PDF Extractor API",
    description="Extract MCQ questions from PDF files and return structured JSON",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "PDF Extract API Running"}

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "MCQ PDF Extractor API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pdf-extractor"}

# Main extraction endpoint
@api_router.post(
    "/extract-questions",
    response_model=ExtractResponse,
    responses={
        200: {"description": "Questions extracted successfully"},
        400: {"model": ErrorResponse, "description": "Invalid file or parsing error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def extract_questions(file: UploadFile = File(...)):
    """
    Extract MCQ questions from uploaded PDF file
    
    - **file**: PDF file containing MCQ questions
    
    Returns JSON with questions, options, and correct answers
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are accepted."
            )
        
        # Read file content
        logger.info(f"Processing file: {file.filename}")
        pdf_bytes = await file.read()
        
        # Check file size (50MB limit)
        if len(pdf_bytes) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 50MB."
            )
        
        # Validate PDF
        if not PDFParser.validate_pdf(pdf_bytes):
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted PDF file."
            )
        
        # Extract text from PDF
        extracted_text = PDFParser.extract_text_from_pdf(pdf_bytes)
        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from PDF. File may be corrupted or empty."
            )
        
        # Parse questions from text
        questions = QuestionExtractor.extract_questions(extracted_text)
        
        if not questions:
            raise HTTPException(
                status_code=400,
                detail="No valid questions found in PDF. Please check the format."
            )
        
        logger.info(f"Successfully extracted {len(questions)} questions from {file.filename}")
        
        return ExtractResponse(
            questions=questions,
            total_questions=len(questions)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
