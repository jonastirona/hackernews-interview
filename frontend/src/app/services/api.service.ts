import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

export interface Story {
  hn_id: string;
  title: string;
  url: string;
  article_url: string;
  points: number;
  author: string;
  comments_count: number;
  full_article_html?: string;
  article_metadata?: any;
  top_comments?: {
    author: string;
    text: string;
    points: number;
  }[];
  analysis?: string;
  hook?: string;
  expanded?: boolean;
  showArticle?: boolean;
  showComments?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8001';
  private eventSource: EventSource | null = null;
  private stories: Story[] = [];
  private isConnecting = false;
  private isComplete = false;
  private hasReceivedData = false;

  constructor() {}

  getStories(offset: number = 0, limit: number = 10): Observable<Story[]> {
    return new Observable<Story[]>(observer => {
      if (this.isConnecting) {
        observer.next([...this.stories]);
        return;
      }

      this.isConnecting = true;
      this.isComplete = false;
      this.hasReceivedData = false;
      
      // Only clear stories if we're starting from the beginning
      if (offset === 0) {
        this.stories = [];
      }

      if (this.eventSource) {
        this.eventSource.close();
      }

      this.eventSource = new EventSource(`${this.apiUrl}/analyze?offset=${offset}&limit=${limit}`);

      // Handle regular data events
      this.eventSource.onmessage = (event) => {
        try {
          const story = JSON.parse(event.data);
          this.hasReceivedData = true;
          this.stories.push({
            ...story,
            expanded: false,
            showArticle: false,
            showComments: false
          });
          observer.next([...this.stories]);
        } catch (error) {
          console.error('Error parsing story data:', error);
        }
      };

      // Handle log events
      this.eventSource.addEventListener('log', (event: MessageEvent) => {
        console.log('Log event:', event.data);
      });

      // Handle error events
      this.eventSource.addEventListener('error', (event: MessageEvent) => {
        // Only treat as error if we haven't received any data or if it's a real error
        if (!this.hasReceivedData || (event.data && !this.isComplete)) {
          if (event.data) {
            try {
              const data = JSON.parse(event.data);
              console.error('Error event:', data);
              observer.error(data);
            } catch (error) {
              console.error('Error parsing error event:', error);
              observer.error(error);
            }
          } else {
            console.error('EventSource error:', event);
            observer.error(event);
          }
        }
        this.cleanup();
      });

      // Handle connection errors
      this.eventSource.onerror = (error) => {
        // Only treat as error if we haven't received any data
        if (!this.hasReceivedData) {
          console.error('EventSource connection error:', error);
          observer.error(error);
        }
        this.cleanup();
      };

      // Handle successful completion
      this.eventSource.addEventListener('complete', () => {
        this.isComplete = true;
        this.cleanup();
        observer.complete();
      });

      return () => {
        this.cleanup();
      };
    });
  }

  private cleanup() {
    if (this.eventSource) {
      console.log('Cleaning up EventSource');
      this.eventSource.close();
      this.eventSource = null;
      this.isConnecting = false;
    }
  }
}
