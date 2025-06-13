import { Component, OnInit, OnDestroy } from '@angular/core';
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
    <div class="min-h-screen bg-gray-50">
      <!-- Header -->
      <header class="bg-white shadow-sm">
        <div class="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 class="text-2xl font-bold text-gray-900">HackerNews OneView</h1>
        </div>
      </header>

      <!-- Main Content -->
      <main class="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Loading State -->
        <app-skeleton-loader *ngIf="loading && stories.length === 0"></app-skeleton-loader>

        <!-- Error Message -->
        <div *ngIf="error" 
             class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-700">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Stories Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <app-story-card *ngFor="let story of stories" 
                         [story]="story">
          </app-story-card>
        </div>

        <!-- Load More Button -->
        <div class="mt-8 flex justify-center">
          <button (click)="loadMoreStories()" 
                  [disabled]="loading"
                  class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200">
            <svg *ngIf="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? 'Loading...' : 'Load More Stories' }}
          </button>
        </div>
      </main>
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }
  `]
})
export class AppComponent implements OnInit, OnDestroy {
  stories: Story[] = [];
  loading = false;
  error: string | null = null;
  offset = 0;
  private subscription: Subscription | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadStories();
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  loadStories() {
    this.loading = true;
    this.error = null;
    
    if (this.subscription) {
      this.subscription.unsubscribe();
    }

    this.subscription = this.apiService.getStories(this.offset, 10).subscribe({
      next: (story) => {
        if (story && story.title) {
          this.stories.push({
            ...story,
            expanded: false,
            showArticle: false,
            showComments: false
          });
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading stories:', error);
        this.error = error.error?.error || 'Error loading stories';
        this.loading = false;
      }
    });
  }

  loadMoreStories() {
    this.offset += 10;
    this.loadStories();
  }

  toggleStory(story: Story) {
    story.expanded = !story.expanded;
  }

  toggleArticle(story: Story) {
    story.showArticle = !story.showArticle;
  }

  toggleComments(story: Story) {
    story.showComments = !story.showComments;
  }
}
