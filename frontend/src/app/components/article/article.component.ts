import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface ScreenshotResponse {
  screenshot_path: string | null;
  message: string | null;
  fallback_html?: string;
}

@Component({
  selector: 'app-article',
  templateUrl: './article.component.html',
  styleUrls: ['./article.component.scss']
})
export class ArticleComponent implements OnInit {
  apiUrl = environment.apiUrl;
  screenshotUrl: string | null = null;
  screenshotError: string | null = null;
  articleContent: string | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {}

  private async loadScreenshot(article: any): Promise<void> {
    if (!article.url) return;

    try {
      const response = await this.http.get<ScreenshotResponse>(
        `${this.apiUrl}/screenshot/${article.id}?url=${encodeURIComponent(article.url)}`
      ).toPromise();

      if (response?.screenshot_path) {
        this.screenshotUrl = `${this.apiUrl}${response.screenshot_path}`;
        this.screenshotError = null;
      } else if (response?.fallback_html) {
        // Handle HTML fallback
        this.screenshotUrl = null;
        this.screenshotError = null;
        this.articleContent = response.fallback_html;
      } else {
        this.screenshotUrl = null;
        this.screenshotError = response?.message || 'Failed to load screenshot';
      }
    } catch (error) {
      console.error('Error loading screenshot:', error);
      this.screenshotUrl = null;
      this.screenshotError = 'Failed to load screenshot';
    }
  }
} 