import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Story } from '../../models/story.model';

@Component({
  selector: 'app-story-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 transition-all duration-200 hover:shadow-md">
      <!-- Story Header -->
      <div class="flex justify-between items-start mb-4">
        <div class="flex-1">
          <h2 class="text-xl font-semibold text-gray-900 mb-2">{{ story.title }}</h2>
          <div class="flex items-center space-x-4 text-sm text-gray-500">
            <span>{{ story.points }} points</span>
            <span>•</span>
            <span>by {{ story.author }}</span>
          </div>
        </div>
        <button (click)="toggleStory()" 
                class="text-gray-400 hover:text-gray-600 transition-colors duration-200">
          <span class="text-xl">{{ story.expanded ? '▲' : '▼' }}</span>
        </button>
      </div>

      <!-- Expanded Content -->
      <div *ngIf="story.expanded" 
           class="space-y-6 animate-expand">
        <!-- Article Section -->
        <div class="border-t border-gray-100 pt-4">
          <button (click)="toggleArticle()" 
                  class="flex items-center text-blue-600 hover:text-blue-700 transition-colors duration-200">
            <span class="text-sm font-medium">{{ story.showArticle ? 'Hide Article' : 'Show Article' }}</span>
            <span class="ml-2 text-lg">{{ story.showArticle ? '▲' : '▼' }}</span>
          </button>
          
          <div *ngIf="story.showArticle" 
               class="mt-4 prose prose-sm sm:prose lg:prose-lg max-w-none">
            <div [innerHTML]="story.full_article_html || 'Loading article content...'"></div>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="border-t border-gray-100 pt-4">
          <button (click)="toggleComments()" 
                  class="flex items-center text-blue-600 hover:text-blue-700 transition-colors duration-200">
            <span class="text-sm font-medium">{{ story.showComments ? 'Hide Comments' : 'Show Comments' }}</span>
            <span class="ml-2 text-lg">{{ story.showComments ? '▲' : '▼' }}</span>
          </button>
          
          <div *ngIf="story.showComments" 
               class="mt-4 space-y-4">
            <div *ngFor="let comment of story.top_comments" 
                 class="bg-gray-50 rounded-lg p-4">
              <div class="font-medium text-blue-600">{{ comment.user }}</div>
              <p class="mt-2 text-gray-700">{{ comment.comment }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    :host {
      display: block;
    }

    .animate-expand {
      animation: expand 0.2s ease-out;
    }

    @keyframes expand {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    :host ::ng-deep .prose img {
      @apply rounded-lg max-w-full h-auto;
    }

    :host ::ng-deep .prose p {
      @apply my-4 leading-relaxed;
    }

    :host ::ng-deep .prose h1,
    :host ::ng-deep .prose h2,
    :host ::ng-deep .prose h3 {
      @apply font-bold text-gray-900 mt-8 mb-4;
    }
  `]
})
export class StoryCardComponent {
  @Input() story!: Story;

  toggleStory() {
    this.story.expanded = !this.story.expanded;
  }

  toggleArticle() {
    this.story.showArticle = !this.story.showArticle;
  }

  toggleComments() {
    this.story.showComments = !this.story.showComments;
  }
} 