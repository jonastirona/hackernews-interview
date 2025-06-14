# Hacker News Reader with AI Analysis

A modern Hacker News reader that uses AI to analyze articles and provide intelligent summaries. Built with Angular and FastAPI, this application enhances the Hacker News experience by adding AI-powered insights and article screenshots.

## Features

- 📰 Real-time Hacker News frontpage scraping
- 🎯 AI-powered article hooks using Google's Gemini API
- 📸 Automatic article screenshots with bot detection bypass
- 💬 Nested comment threading
- 🎯 Smart content extraction and formatting
- 🔄 Server-sent events for real-time updates
- 🎨 Modern, responsive UI

## Tech Stack

### Frontend
- Angular 17 (Standalone Components)
- TypeScript
- TailwindCSS
- RxJS for reactive state management

### Backend
- FastAPI
- Playwright for web scraping
- Google Gemini API for article hooks
- BeautifulSoup4 for HTML parsing
- Server-sent events for streaming

## Architecture

### Data Flow
1. **Frontend Request**
   - User loads the application
   - Angular service makes SSE connection to backend
   - Initial batch of stories requested

2. **Backend Processing**
   ```
   Frontend Request
   ↓
   FastAPI Endpoint
   ↓
   Hacker News Scraper
   ↓
   Article Content Scraper
   ↓
   Screenshot Manager
   ↓
   Gemini API Hook Generation
   ↓
   SSE Stream to Frontend
   ```

3. **AI Analysis Pipeline**
   - Article content is extracted and cleaned
   - Screenshot is captured with anti-bot measures
   - Content is sent to Gemini API for:
     - Article hook generation (2-3 sentence summary)
     - Basic article analysis with comments

## Directory Structure

```
hackernews-interview/
├── backend/                    # FastAPI backend
│   ├── cache/                 # Article and screenshot cache
│   ├── static/               # Static files (screenshots)
│   ├── utils/                # Utility modules
│   │   ├── scraper.py       # Web scraping utilities
│   │   └── gemini.py        # Gemini API integration
│   ├── main.py              # FastAPI application entry
│   ├── stream.py            # SSE streaming implementation
│   ├── screenshot.py        # Screenshot management
│   └── requirements.txt     # Python dependencies
│
├── frontend/                  # Angular frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/  # Angular components
│   │   │   │   ├── story-card/      # Story display component
│   │   │   │   └── skeleton-loader/ # Loading state component
│   │   │   ├── models/      # TypeScript interfaces
│   │   │   ├── services/    # API and data services
│   │   │   └── app.component.ts     # Main application component
│   │   └── assets/         # Static assets
│   ├── package.json        # Node.js dependencies
│   └── angular.json        # Angular configuration
│
└── README.md               # Project documentation
```

### Key Directories Explained

#### Backend
- `cache/`: Stores processed article data and screenshots
- `static/`: Serves static files like screenshots
- `utils/`: Core functionality modules
  - `scraper.py`: Handles web scraping
  - `gemini.py`: Manages AI analysis
- `main.py`: API endpoints and application setup
- `stream.py`: Server-sent events implementation
- `screenshot.py`: Screenshot capture and management

#### Frontend
- `components/`: Reusable UI components
  - `story-card/`: Displays individual stories
  - `skeleton-loader/`: Loading state UI
- `models/`: TypeScript interfaces and types
- `services/`: API integration and data management
- `app.component.ts`: Main application logic

## Current Implementation Details

### Resource Management
- Basic browser instance management with Playwright
- Error handling and recovery for failed requests
- Timeout handling for API calls (30 seconds)

### API Integration
- Direct integration with Google's Gemini API
- Basic async processing using Python's asyncio
- File-based caching for article data and screenshots
- Error handling for API failures

### Caching
- File system caching for article content and screenshots
- Browser cache headers for static assets
- Basic cache validation and cleanup

### Concurrency
- Async/await implementation for non-blocking operations
- Server-sent events for real-time updates
- Basic error handling and reconnection logic

## Future Improvements

1. **Performance**
   - Client-side caching
   - Progressive image loading
   - Optimized bundle size
   - Service worker for offline support

2. **Features**
   - User authentication
   - Saved articles
   - Custom feeds
   - Share functionality

3. **Scaling**
   - Worker pool for parallel processing
   - Request batching for API calls
   - Advanced response caching
   - Rate limiting implementation
   - Connection pooling
   - Job-based request tracking
   - User session management
   - Resource allocation per user
   - Queue prioritization

## Development

### Prerequisites
- Python 3.8+
- Node.js 18+
- Playwright browsers
- Google Cloud API key

### Setup
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
uvicorn main:app --reload

# Frontend
cd frontend
npm install
ng serve
```

### Environment Variables
```env
# Backend
GOOGLE_API_KEY=your_gemini_api_key
CORS_ORIGINS=http://localhost:4200

# Frontend
API_URL=http://localhost:8001
```

## Testing
```bash
# Backend
pytest

# Frontend
ng test
```

## Credits

- Original repository: [RA-Trio/hackernews-interview](https://github.com/RA-Trio/hackernews-interview)

## License

MIT License - see LICENSE file for details
