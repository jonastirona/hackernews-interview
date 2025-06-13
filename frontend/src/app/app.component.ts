/**
 * Main application component for the Hacker News reader.
 * 
 * This component manages:
 * - Story loading and pagination
 * - Error handling and retry functionality
 * - Story card rendering and state management
 * - Comment loading and pagination
 */
import { Component, OnInit, OnDestroy, ViewChildren, QueryList } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from './services/api.service';
import { Story } from './models/story.model';
import { SkeletonLoaderComponent } from './components/skeleton-loader/skeleton-loader.component';
import { StoryCardComponent } from './components/story-card/story-card.component';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, SkeletonLoaderComponent, StoryCardComponent],
  template: `
    <div class="container">
      <header>
        <h1>Hacker News Articles</h1>
      </header>

      <main>
        <!-- Error message display with retry option -->
        <div *ngIf="error" class="error-message">
          <span class="error-icon">⚠️</span>
          {{ error }}
          <button *ngIf="error" (click)="retry()" class="retry-button">
            Retry
          </button>
        </div>

        <!-- Loading state indicator -->
        <div *ngIf="loading && stories.length === 0" class="loading">
          Loading stories...
        </div>

        <!-- Stories list with pagination -->
        <div *ngIf="!error" class="stories">
          <app-story-card
            *ngFor="let story of stories"
            [story]="story"
            (loadMoreComments)="onLoadMoreComments($event)">
          </app-story-card>

          <!-- Load more button -->
          <button
            *ngIf="stories.length > 0 && hasMoreStories"
            (click)="loadMoreStories()"
            [disabled]="loading"
            class="load-more">
            {{ loading ? 'Loading...' : 'Load More Stories' }}
          </button>
          <div *ngIf="!hasMoreStories && stories.length > 0" class="no-more-stories">
            No more stories to load
          </div>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }

    header {
      text-align: center;
      margin-bottom: 2rem;
    }

    h1 {
      font-size: 2.5rem;
      color: #1a1a1a;
      margin: 0;
    }

    .error-message {
      background-color: #fff5f5;
      border-left: 4px solid #f56565;
      padding: 1rem;
      margin-bottom: 1rem;
      color: #c53030;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .error-icon {
      font-size: 1.2rem;
    }

    .retry-button {
      margin-left: auto;
      padding: 0.5rem 1rem;
      background-color: #f56565;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.9rem;
      transition: background-color 0.2s;
    }

    .retry-button:hover {
      background-color: #e53e3e;
    }

    .loading {
      text-align: center;
      padding: 2rem;
      color: #666;
    }

    .stories {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .load-more {
      margin-top: 2rem;
      padding: 0.75rem 1.5rem;
      background-color: #0066cc;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.2s;
    }

    .load-more:hover:not(:disabled) {
      background-color: #0052a3;
    }

    .load-more:disabled {
      background-color: #ccc;
      cursor: not-allowed;
    }

    .no-more-stories {
      text-align: center;
      color: #666;
      font-size: 0.9rem;
      margin-top: 2rem;
      padding: 1rem;
      background: #f5f5f5;
      border-radius: 4px;
    }
  `]
})
export class AppComponent implements OnInit, OnDestroy {
  /** Reference to all story card components */
  @ViewChildren(StoryCardComponent) storyCards!: QueryList<StoryCardComponent>;
  
  /** Array of stories to display */
  stories: Story[] = [];
  
  /** Loading state indicator */
  loading = false;
  
  /** Error message if any */
  error: string | null = null;
  
  /** Subscription to API calls */
  private subscription: Subscription | null = null;
  
  /** Current pagination offset */
  private offset = 0;
  
  /** Number of stories to load per page */
  private limit = 10;
  
  /** Flag indicating if more stories are available */
  hasMoreStories = true;

  constructor(private apiService: ApiService) {}

  /**
   * Initialize component and load initial stories
   */
  ngOnInit() {
    this.loadStories();
  }

  /**
   * Clean up subscriptions when component is destroyed
   */
  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  /**
   * Load stories from the API
   * Handles both initial load and pagination
   */
  loadStories() {
    this.loading = true;
    this.error = null;

    if (this.subscription) {
      this.subscription.unsubscribe();
    }

    this.subscription = this.apiService.getStories(this.offset, this.limit).subscribe({
      next: (newStories) => {
        if (this.offset === 0) {
          this.stories = newStories;
        } else {
          const existingIds = new Set(this.stories.map(s => s.hn_id));
          const uniqueNewStories = newStories.filter(s => !existingIds.has(s.hn_id));
          this.stories = [...this.stories, ...uniqueNewStories];
        }
        this.loading = false;
        this.hasMoreStories = this.apiService.canLoadMoreStories();
      },
      error: (err) => {
        this.error = 'Error loading stories. Please try again later.';
        this.loading = false;
        console.error('Error loading stories:', err);
      },
      complete: () => {
        this.loading = false;
        this.stories = this.apiService.getCurrentStories();
      }
    });
  }

  /**
   * Load more stories by incrementing the offset
   */
  loadMoreStories() {
    if (!this.loading && this.hasMoreStories) {
      this.offset += this.limit;
      this.loadStories();
    }
  }

  /**
   * Retry loading stories after an error
   */
  retry() {
    this.error = null;
    this.loadStories();
  }

  /**
   * Handle loading more comments for a story
   * @param event Object containing storyId and offset
   */
  async onLoadMoreComments(event: {storyId: string, offset: number}) {
    try {
      const result = await this.apiService.loadMoreComments(event.storyId, event.offset);
      this.stories = result.stories;
    } catch (error) {
      console.error('Error loading more comments:', error);
    }
  }

  /**
   * Toggle story expansion state
   * @param story Story to toggle
   */
  toggleStory(story: Story) {
    story.expanded = !story.expanded;
  }

  /**
   * Toggle article visibility
   * @param story Story to toggle article for
   */
  toggleArticle(story: Story) {
    story.showArticle = !story.showArticle;
  }

  /**
   * Toggle comments visibility
   * @param story Story to toggle comments for
   */
  toggleComments(story: Story) {
    story.showComments = !story.showComments;
  }
}
