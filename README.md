# Hacker News Reader with AI Analysis

A modern Hacker News reader that uses AI to analyze articles and provide intelligent summaries. Built with Angular and FastAPI, this application enhances the Hacker News experience by adding AI-powered insights and article screenshots.

## Features

- 📰 Real-time Hacker News frontpage scraping
- �� AI-powered article hooks using Google's Gemini API
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

## Future Improvements

1. **Content Enhancement**
   - Support for comment sorting and filtering
   - Pagination beyond 30 articles
   - Article image/favicon display
   - Related articles suggestions

2. **UI/UX Improvements**
   - Dark mode support
   - Mobile-first responsive design
   - Keyboard navigation
   - Customizable feed preferences

3. **Performance**
   - Client-side caching
   - Progressive image loading
   - Optimized bundle size
   - Service worker for offline support

4. **Features**
   - User authentication
   - Saved articles
   - Custom feeds
   - Share functionality

## Scaling Strategy

### Resource Management
- **Playwright Sessions**
  - Async queue for browser instances
  - Connection pooling
  - Automatic cleanup
  - Error recovery

### API Optimization
- **Gemini API**
  - Worker pool for parallel processing
  - Request batching
  - Response caching
  - Rate limiting

### Anti-Ban Measures
- Domain-specific rate limiting
- Rotating user agents
- Request delays
- IP rotation support

### Caching Strategy
- File system for article content and screenshots
- Memory cache for API responses
- Browser cache headers

### Concurrency
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
- AI powered by [Google Gemini API](https://ai.google.dev/)
- Built by Jonas

## License

MIT License - see LICENSE file for details
