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

### 2. Process Resume with Streaming
```bash
GET /process_node?id=<thread_id>&message=<resume_text>
```

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

2. Process resume with streaming:
```bash
curl -N "http://localhost:8000/process_node?id=123&message=John%20Doe%20Software%20Engineer..."
```

### Using JavaScript

```javascript
// Get next question
const response = await fetch('http://localhost:8000/resume_question?id=123');
const data = await response.json();
console.log(data.question);

// Process resume with streaming
const eventSource = new EventSource(
  'http://localhost:8000/process_node?id=123&message=John%20Doe%20Software%20Engineer...'
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.summary) {
    console.log('Summary:', data.summary);
  } else if (data.question) {
    console.log('Question:', data.question);
  }
};
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