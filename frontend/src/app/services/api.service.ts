import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { Story } from '../models/story.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8001';
  private stories: Story[] = [];
  private eventSource: EventSource | null = null;
  private isConnecting = false;
  private isComplete = false;
  private hasReceivedData = false;
  private hasMoreStories = true;

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
        this.hasMoreStories = true;
      }

      if (!this.hasMoreStories) {
        observer.next([...this.stories]);
        observer.complete();
        return;
      }

      this.eventSource = new EventSource(`${this.apiUrl}/analyze?offset=${offset}&limit=${limit}`);

      // Handle regular data events
      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.hasReceivedData = true;
          
          // Update has_more flag
          if (data.has_more !== undefined) {
            this.hasMoreStories = data.has_more;
          }
          
          // Find if story already exists
          const existingStoryIndex = this.stories.findIndex(s => s.hn_id === data.hn_id);
          
          if (existingStoryIndex === -1) {
            // New story
            this.stories.push({
              ...data,
              expanded: false,
              showArticle: false,
              showComments: false
            });
          } else {
            // Update existing story
            this.stories[existingStoryIndex] = {
              ...this.stories[existingStoryIndex],
              ...data
            };
          }
          
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
        if (!this.isComplete) {
          observer.error('Connection error');
        }
        this.cleanup();
      });

      // Handle complete event
      this.eventSource.addEventListener('complete', () => {
        this.isComplete = true;
        this.cleanup();
        observer.complete();
      });

      // Return cleanup function
      return () => {
        this.cleanup();
      };
    });
  }

  async loadMoreComments(storyId: string, offset: number): Promise<{stories: Story[], hasMore: boolean}> {
    try {
      const response = await fetch(`${this.apiUrl}/debug/comments?id=${storyId}&offset=${offset}`);
      const data = await response.json();
      
      // Find the story and update its comments
      const storyIndex = this.stories.findIndex(s => s.hn_id === storyId);
      if (storyIndex !== -1) {
        const story = this.stories[storyIndex];
        const existingComments = story.top_comments || [];
        
        // Filter out any potential duplicates based on author and text
        const existingCommentKeys = new Set(
          existingComments.map(c => `${c.author}:${c.text}`)
        );
        
        const uniqueNewComments = data.comments.filter(
          (c: any) => !existingCommentKeys.has(`${c.author}:${c.text}`)
        );
        
        story.top_comments = [...existingComments, ...uniqueNewComments];
        this.stories[storyIndex] = story;
      }
      
      return {
        stories: [...this.stories],
        hasMore: data.has_more
      };
    } catch (error) {
      console.error('Error loading more comments:', error);
      throw error;
    }
  }

  canLoadMoreStories(): boolean {
    return this.hasMoreStories;
  }

  private cleanup() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.isConnecting = false;
  }
}
