# MCQ PDF Extractor API

A FastAPI-based service that extracts Multiple Choice Questions (MCQ) from PDF files and returns structured JSON data.

## Features

- ✅ Extract questions, options, and correct answers from PDF files
- ✅ Support for multi-page PDFs
- ✅ No LLM/AI APIs required - uses PyMuPDF for parsing
- ✅ RESTful API with Swagger documentation
- ✅ Comprehensive error handling
- ✅ Production-ready with Docker support

## Tech Stack

- **Python 3.11**
- **FastAPI** - Modern web framework
- **PyMuPDF (fitz)** - PDF text extraction
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## PDF Format Requirements

Your PDF should follow this structure:

```
1. What is the capital of France?
a) London
b) Berlin
# c) Paris
d) Madrid

2. Which planet is known as the Red Planet?
a) Venus
b) Jupiter
# c) Mars
d) Saturn
```

**Format Rules:**
- Questions must be numbered (1. 2. 3. etc.)
- Options must use letters a), b), c), d)
- Correct answer must be marked with `#` at the start of the line
- Exactly 4 options per question

## Installation

### Option 1: Local Setup

```bash
# Clone the repository
cd /app/backend

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Option 2: Docker

```bash
# Build the image
docker build -t mcq-extractor .

# Run the container
docker run -p 8001:8001 mcq-extractor
```

## API Endpoints

### 1. Extract Questions

**POST** `/api/extract-questions`

Upload a PDF file and extract MCQ questions.

**Request:**
```bash
curl -X POST "http://localhost:8001/api/extract-questions" \
  -F "file=@sample.pdf" \
  -H "Accept: application/json"
```

**Response:**
```json
{
  "questions": [
    {
      "question": "What is the capital of France?",
      "options": ["London", "Berlin", "Paris", "Madrid"],
      "answer": "Paris"
    }
  ],
  "total_questions": 1
}
```

### 2. Health Check

**GET** `/api/health`

```bash
curl http://localhost:8001/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "pdf-extractor"
}
```

### 3. API Documentation

Interactive Swagger documentation available at:
```
http://localhost:8001/docs
```

## Usage Examples

### Python Example

```python
import requests

url = "http://localhost:8001/api/extract-questions"
files = {"file": open("sample.pdf", "rb")}
response = requests.post(url, files=files)

data = response.json()
print(f"Found {data['total_questions']} questions")
for q in data['questions']:
    print(f"Q: {q['question']}")
    print(f"Answer: {q['answer']}")
```

### Java Spring Boot Example

```java
RestTemplate restTemplate = new RestTemplate();

HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.MULTIPART_FORM_DATA);

MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
body.add("file", new FileSystemResource("sample.pdf"));

HttpEntity<MultiValueMap<String, Object>> requestEntity = 
    new HttpEntity<>(body, headers);

ResponseEntity<JsonNode> response = restTemplate.postForEntity(
    "http://localhost:8001/api/extract-questions",
    requestEntity,
    JsonNode.class
);

JsonNode data = response.getBody();
System.out.println("Total questions: " + data.get("total_questions"));
```

### cURL Example

```bash
# Extract questions from PDF
curl -X POST "http://localhost:8001/api/extract-questions" \
  -F "file=@/path/to/questions.pdf" \
  -H "Accept: application/json" | jq
```

## Error Handling

The API returns appropriate HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success - questions extracted |
| 400 | Bad Request - invalid file, format error, no questions found |
| 500 | Internal Server Error |

**Error Response Example:**
```json
{
  "detail": "Invalid file type. Only PDF files are accepted."
}
```

## Performance

- ✅ Handles PDFs up to 50MB
- ✅ Processes ~10 pages in < 3 seconds
- ✅ Streaming upload for memory efficiency

## Project Structure

```
backend/
├── server.py              # Main FastAPI application
├── models.py              # Pydantic data models
├── pdf_parser.py          # PDF text extraction using PyMuPDF
├── question_extractor.py  # Question parsing logic
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── README.md             # This file
```

## Environment Variables

```bash
# Optional configuration
CORS_ORIGINS="*"  # Comma-separated list of allowed origins
```

## Testing

Test the API with sample PDFs:

```bash
# Create a test PDF (requires reportlab)
python3 << 'EOF'
from reportlab.pdfgen import canvas

c = canvas.Canvas("test.pdf")
c.drawString(50, 750, "1. Sample question?")
c.drawString(50, 730, "a) Option A")
c.drawString(50, 710, "# b) Option B")
c.drawString(50, 690, "c) Option C")
c.drawString(50, 670, "d) Option D")
c.save()
EOF

# Test the endpoint
curl -X POST "http://localhost:8001/api/extract-questions" \
  -F "file=@test.pdf" | jq
```

## Integration with Java Backend

**Flow:**
1. Java Spring Boot receives PDF upload from frontend
2. Java sends PDF to Python FastAPI service via `/api/extract-questions`
3. Python extracts and parses questions
4. Python returns JSON to Java
5. Java stores questions in database (PostgreSQL/MySQL)
6. Java serves data to frontend

**Java Service Example:**
```java
@Service
public class QuestionService {
    
    @Value("${python.service.url}")
    private String pythonServiceUrl;
    
    public QuestionResponse extractQuestions(MultipartFile file) {
        RestTemplate restTemplate = new RestTemplate();
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", file.getResource());
        
        HttpEntity<MultiValueMap<String, Object>> request = 
            new HttpEntity<>(body, headers);
        
        return restTemplate.postForObject(
            pythonServiceUrl + "/api/extract-questions",
            request,
            QuestionResponse.class
        );
    }
}
```

## Troubleshooting

### Issue: "Failed to extract text from PDF"
- Ensure PDF is not corrupted
- Check if PDF contains actual text (not scanned images)
- Verify PDF is not password-protected

### Issue: "No valid questions found"
- Verify PDF follows the required format
- Check that questions are numbered (1. 2. 3.)
- Ensure options use a) b) c) d) format
- Confirm correct answer is marked with #

### Issue: "Question has X options instead of 4"
- Each question must have exactly 4 options
- Ensure no extra letters or formatting

## Security Considerations

- ✅ File type validation (PDF only)
- ✅ File size limit (50MB)
- ✅ Text sanitization during extraction
- ✅ CORS configuration for allowed origins

## License

MIT License

## Support

For issues or questions, please check:
- API Documentation: http://localhost:8001/docs
- Health Check: http://localhost:8001/api/health
