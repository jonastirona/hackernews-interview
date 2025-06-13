import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Story } from '../../models/story.model';

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
          <div [innerHTML]="story.full_article_html"></div>
        </div>

        <div class="comments-section" *ngIf="showComments">
          <div class="comment" *ngFor="let comment of story.top_comments">
            <div class="comment-meta">
              <span class="comment-author">{{ comment.author }}</span>
              <span class="comment-points">{{ comment.points }} points</span>
            </div>
            <div class="comment-text" [innerHTML]="comment.text"></div>
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

    .comments-section {
      margin-top: 1rem;
    }

    .comment {
      padding: 1rem;
      background: #f9f9f9;
      border-radius: 4px;
      margin-bottom: 0.5rem;
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
  `]
})
export class StoryCardComponent {
  @Input() story!: Story;
  showArticle = false;
  showComments = false;

  toggleArticle() {
    this.showArticle = !this.showArticle;
  }

  toggleComments() {
    this.showComments = !this.showComments;
  }
} 