import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { Story } from '../models/story.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8001';
  private eventSource: EventSource | null = null;
  private eventSubject = new Subject<any>();

  constructor() {}

  getStories(offset: number = 0, limit: number = 10): Observable<Story> {
    if (this.eventSource) {
      this.eventSource.close();
    }

    this.eventSource = new EventSource(`${this.apiUrl}/analyze?offset=${offset}&limit=${limit}`);

    return new Observable<Story>(observer => {
      // Handle regular data events
      this.eventSource!.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          observer.next(data);
        } catch (error) {
          console.error('Error parsing event data:', error);
        }
      };

      // Handle log events
      this.eventSource!.addEventListener('log', (event: MessageEvent) => {
        console.log('Log event:', event.data);
      });

      // Handle error events
      this.eventSource!.addEventListener('error', (event: MessageEvent) => {
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
        this.cleanup();
      });

      // Handle connection errors
      this.eventSource!.onerror = (error) => {
        console.error('EventSource connection error:', error);
        observer.error(error);
        this.cleanup();
      };

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
    }
  }
}
