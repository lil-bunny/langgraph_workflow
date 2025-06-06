# AI Interview Assistant

An intelligent interview assistant that processes resumes and generates relevant interview questions using LangChain and Google's Gemini model.

## Architecture

The system is built using a graph-based architecture with the following components:

### Core Components

1. **ResumeGraph Class**
   - Manages the processing pipeline using LangGraph
   - Handles state management and graph execution
   - Integrates with Google's Gemini model for AI processing

2. **Processing Pipeline**
   - Work Experience Parser
   - Education Parser
   - Resume Summarizer
   - Insight Extractor
   - Question Generator

3. **State Management**
   - Uses LangGraph's MemorySaver for state persistence
   - Maintains separate states for different interview sessions
   - Tracks interview questions and resume insights

### Data Models

- `ResumeMode`: Main state model containing:
  - Resume text
  - Work experience
  - Education details
  - Resume insights
  - Interview questions

- Supporting models:
  - `WorkExperience`
  - `Education`
  - `ResumeInsight`
  - `InterviewQuestion`

## API Endpoints

### 1. Get Next Question
```bash
GET /resume_question?id=<thread_id>
```

**Response:**
```json
{
    "question": "What experience do you have with microservices architecture?"
}
```

### 2. Analyze Resume with Streaming (Text)
```bash
POST /analyze-resume?id=<thread_id>&resume_text=<resume_text>
```

**Parameters:**
- `id`: Thread ID (required, query parameter)
- `resume_text`: Resume text to process (required, query parameter)

**Response:** Server-Sent Events (SSE) stream containing:
```json
{"summary": "Candidate has 5 years of experience..."}
{"question": "How did you handle the migration to microservices?"}
```

### 3. Analyze Resume with Streaming (PDF)
```bash
POST /analyze-resume-pdf?id=<thread_id>
Content-Type: multipart/form-data
```

**Request Body:**
- `file`: PDF resume file (required)
- `id`: Thread ID (required, query parameter)

**Response:** Server-Sent Events (SSE) stream containing:
```json
{"summary": "Candidate has 5 years of experience..."}
{"question": "How did you handle the migration to microservices?"}
```

## Setup and Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# .env
GOOGLE_API_KEY=your_gemini_api_key
```

3. Run the server:
```bash
uvicorn app:app --reload
```

## Example Usage

### Using curl

1. Get next question:
```bash
curl "http://localhost:8000/resume_question?id=123"
```

2. Analyze resume with streaming (Text):
```bash
curl -N -X POST "http://localhost:8000/analyze-resume?id=123&resume_text=John%20Doe%20Software%20Engineer%20with%205%20years%20of%20experience..."
```

3. Analyze resume with streaming (PDF):
```bash
curl -N -X POST "http://localhost:8000/analyze-resume-pdf?id=123" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"
```

### Using JavaScript

```javascript
// Get next question
const response = await fetch('http://localhost:8000/resume_question?id=123');
const data = await response.json();
console.log(data.question);

// Analyze resume with streaming (Text)
const resumeText = "John Doe\nSoftware Engineer\n5 years of experience...";
const encodedResume = encodeURIComponent(resumeText);

const textEventSource = new EventSource(
  `http://localhost:8000/analyze-resume?id=123&resume_text=${encodedResume}`
);

// Analyze resume with streaming (PDF)
const formData = new FormData();
formData.append('file', pdfFile); // pdfFile is a File object from input[type="file"]

const pdfEventSource = new EventSource(
  `http://localhost:8000/analyze-resume-pdf?id=123&file=${encodeURIComponent(pdfFile.name)}`
);

// Send the file using fetch
await fetch(`http://localhost:8000/analyze-resume-pdf?id=123`, {
  method: 'POST',
  body: formData
});

// Handle messages for both PDF and text analysis
const handleMessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.summary) {
    console.log('Summary:', data.summary);
  } else if (data.question) {
    console.log('Question:', data.question);
  }
};

textEventSource.onmessage = handleMessage;
pdfEventSource.onmessage = handleMessage;

// Handle errors
const handleError = (error) => {
  console.error('EventSource failed:', error);
  textEventSource.close();
  pdfEventSource.close();
};

textEventSource.onerror = handleError;
pdfEventSource.onerror = handleError;
```

## Error Handling

The API returns appropriate error messages in the following format:
```json
{
    "error": "Error message description"
}
```

Common error scenarios:
- Invalid thread ID
- No questions available
- Processing errors
- State management errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 