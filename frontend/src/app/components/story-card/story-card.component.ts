import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Story } from '../../models/story.model';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-story-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="story-card">
      <div class="story-header">
        <h3 class="story-title">
          <a [href]="story.article_url" target="_blank" rel="noopener noreferrer">
            {{ story.title }}
          </a>
          <span class="story-discussion">
            <a [href]="story.url" target="_blank" rel="noopener noreferrer">
              (discuss)
            </a>
          </span>
        </h3>
        <div class="story-meta">
          <span class="points">{{ story.points }} points</span>
          <span class="author">by {{ story.author }}</span>
          <span class="comments">{{ story.comments_count }} comments</span>
        </div>
      </div>
      
      <div class="story-content">
        <p class="story-hook" *ngIf="story.hook">{{ story.hook }}</p>
        
        <div class="story-actions">
          <button 
            class="action-button"
            [class.active]="showArticle"
            (click)="toggleArticle()">
            {{ showArticle ? 'Hide Article' : 'Show Article' }}
          </button>
          <button 
            class="action-button"
            [class.active]="showComments"
            (click)="toggleComments()">
            {{ showComments ? 'Hide Comments' : 'Show Comments' }}
          </button>
        </div>

        <div class="article-content" *ngIf="showArticle">
          <div *ngIf="screenshotError" class="screenshot-error">
            <p>{{ screenshotError }}</p>
            <a [href]="story.article_url" target="_blank" rel="noopener noreferrer" class="view-original">
              View original article
            </a>
          </div>
          <div *ngIf="isLoading && !screenshotError" class="loading-screenshot">
            <div class="spinner"></div>
            <p>Loading screenshot...</p>
          </div>
          <div *ngIf="screenshotUrl && !screenshotError" class="screenshot-container">
            <img [src]="screenshotUrl" 
                 [alt]="story.title"
                 class="article-screenshot"
                 (error)="onScreenshotError()">
          </div>
        </div>

        <div class="comments-section" *ngIf="showComments">
          <div class="comment" *ngFor="let comment of story.top_comments" [style.margin-left.px]="comment.depth * 20">
            <div class="comment-meta">
              <span class="comment-author">{{ comment.author }}</span>
            </div>
            <div class="comment-text" [innerHTML]="comment.text"></div>
          </div>
          
          <button 
            *ngIf="story.top_comments && story.top_comments.length < story.comments_count && hasMoreComments"
            (click)="onLoadMoreComments()"
            class="load-more-comments">
            Load More Comments
          </button>
          <div *ngIf="!hasMoreComments && story.top_comments && story.top_comments.length > 0" class="no-more-comments">
            No more comments to load
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .story-card {
      background: white;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .story-header {
      margin-bottom: 1rem;
    }

    .story-title {
      margin: 0;
      font-size: 1.2rem;
      line-height: 1.4;
    }

    .story-title a {
      color: #1a1a1a;
      text-decoration: none;
    }

    .story-title a:hover {
      color: #0066cc;
    }

    .story-discussion {
      font-size: 0.9rem;
      color: #666;
      margin-left: 0.5rem;
    }

    .story-discussion a {
      color: #666;
      text-decoration: none;
    }

    .story-discussion a:hover {
      color: #0066cc;
    }

    .story-meta {
      font-size: 0.9rem;
      color: #666;
      margin-top: 0.5rem;
    }

    .story-meta span {
      margin-right: 1rem;
    }

    .story-content {
      margin-top: 1rem;
    }

    .story-hook {
      font-size: 1rem;
      line-height: 1.5;
      color: #444;
      margin-bottom: 1rem;
      font-style: italic;
    }

    .story-actions {
      display: flex;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .action-button {
      padding: 0.5rem 1rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      background: white;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s;
    }

    .action-button:hover {
      background: #f5f5f5;
    }

    .action-button.active {
      background: #0066cc;
      color: white;
      border-color: #0066cc;
    }

    .article-content {
      margin-top: 1rem;
      padding: 1rem;
      background: #f9f9f9;
      border-radius: 4px;
    }

    .screenshot-container {
      position: relative;
      width: 100%;
      overflow: hidden;
      border-radius: 4px;
      background: #fff;
    }

    .article-screenshot {
      width: 100%;
      height: auto;
      display: block;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .screenshot-error {
      padding: 2rem;
      text-align: center;
      color: #666;
      background: #f5f5f5;
      border-radius: 4px;
    }

    .screenshot-error a {
      color: #0066cc;
      text-decoration: none;
    }

    .screenshot-error a:hover {
      text-decoration: underline;
    }

    .loading-screenshot {
      padding: 2rem;
      text-align: center;
      color: #666;
      background: #f5f5f5;
      border-radius: 4px;
    }

    .comments-section {
      margin-top: 1rem;
    }

    .comment {
      padding: 1rem;
      background: #f9f9f9;
      border-radius: 4px;
      margin-bottom: 0.5rem;
      border-left: 2px solid #e0e0e0;
    }

    .comment-meta {
      font-size: 0.9rem;
      color: #666;
      margin-bottom: 0.5rem;
    }

    .comment-author {
      font-weight: bold;
      margin-right: 1rem;
    }

    .comment-text {
      font-size: 0.95rem;
      line-height: 1.5;
    }

    .load-more-comments {
      width: 100%;
      padding: 0.75rem;
      margin-top: 1rem;
      background: #f5f5f5;
      border: 1px solid #ddd;
      border-radius: 4px;
      color: #666;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.2s;
    }

    .load-more-comments:hover {
      background: #e5e5e5;
    }

    .no-more-comments {
      text-align: center;
      color: #666;
      font-size: 0.9rem;
      margin-top: 1rem;
      padding: 0.5rem;
      background: #f5f5f5;
      border-radius: 4px;
    }
  `]
})
export class StoryCardComponent implements OnInit, OnChanges {
  @Input() story!: Story;
  @Output() loadMoreComments = new EventEmitter<{storyId: string, offset: number}>();
  
  showArticle = false;
  showComments = false;
  commentsOffset = 0;
  hasMoreComments = true;
  screenshotError: string | null = null;
  screenshotUrl: string | null = null;
  isLoading = false;

  constructor() {}

  ngOnInit() {
    if (this.story) {
      this.loadScreenshot();
    }
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['story'] && changes['story'].currentValue) {
      this.loadScreenshot();
    }
  }

  toggleArticle() {
    this.showArticle = !this.showArticle;
    if (this.showArticle) {
      this.showComments = false;
      this.loadScreenshot();
    }
  }

  toggleComments() {
    this.showComments = !this.showComments;
    if (this.showComments) {
      this.showArticle = false;
    }
  }

  onLoadMoreComments() {
    this.commentsOffset += 10;
    this.loadMoreComments.emit({
      storyId: this.story.hn_id,
      offset: this.commentsOffset
    });
  }

  updateComments(hasMore: boolean) {
    this.hasMoreComments = hasMore;
  }

  onScreenshotError() {
    this.screenshotError = "Failed to load screenshot - Please visit the article directly";
    this.isLoading = false;
    this.screenshotUrl = null;
  }

  getScreenshotUrl(): string {
    if (!this.story.screenshot_path) return '';
    return `${environment.apiUrl}${this.story.screenshot_path}`;
  }

  private loadScreenshot() {
    if (!this.story?.screenshot_path) {
      this.screenshotError = this.story?.screenshot_error || "Screenshot unavailable";
      this.isLoading = false;
      this.screenshotUrl = null;
      return;
    }

    this.isLoading = true;
    this.screenshotError = null;
    this.screenshotUrl = this.getScreenshotUrl();
  }

  getDomain(url: string): string {
    try {
      const domain = new URL(url).hostname;
      return domain.replace('www.', '');
    } catch {
      return url;
    }
  }

  getTimeAgo(timestamp: number): string {
    const seconds = Math.floor((Date.now() - timestamp * 1000) / 1000);
    if (seconds < 60) return `${seconds} seconds ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes} minute${minutes === 1 ? '' : 's'} ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours === 1 ? '' : 's'} ago`;
    const days = Math.floor(hours / 24);
    return `${days} day${days === 1 ? '' : 's'} ago`;
  }
} 