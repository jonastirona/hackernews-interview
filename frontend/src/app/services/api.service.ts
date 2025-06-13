import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor() {}

  getArticles(offset: number = 0, limit: number = 10): Observable<any> {
    return new Observable(observer => {
      console.log('Starting to fetch articles...');
      const eventSource = new EventSource(`/analyze?offset=${offset}&limit=${limit}`);

      // Handle regular data events
      eventSource.onmessage = (event) => {
        try {
          console.log('Received event:', event.data);
          const data = JSON.parse(event.data);
          if (data && data.title) {
            console.log('Parsed story:', data);
            observer.next(data);
          } else {
            console.warn('Received invalid story data:', data);
          }
        } catch (error) {
          console.error('Error parsing story data:', error);
        }
      };

      // Handle log events
      eventSource.addEventListener('log', (event: MessageEvent) => {
        console.log('Log event:', event.data);
      });

      // Handle error events
      eventSource.addEventListener('error', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          console.error('Error event:', data);
          observer.error(data);
        } catch (error) {
          console.error('Error parsing error event:', error);
        }
      });

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        observer.error(error);
        eventSource.close();
      };

      return () => {
        console.log('Cleaning up EventSource');
        eventSource.close();
      };
    });
  }
}
