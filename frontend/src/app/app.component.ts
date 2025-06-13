import { Component, OnInit } from '@angular/core';
import { ApiService } from './services/api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,
  imports: [CommonModule]
})
export class AppComponent implements OnInit {
  stories: any[] = [];
  offset = 0;
  isLoading = false;

  constructor(private api: ApiService) {
    console.log('AppComponent initialized');
  }

  ngOnInit() {
    console.log('AppComponent ngOnInit');
    this.loadMore();
  }

  loadMore() {
    console.log('Loading more stories, offset:', this.offset);
    this.isLoading = true;
    this.api.getArticles(this.offset).subscribe({
      next: (data) => {
        console.log('Received story in component:', data);
        // Initialize expanded state
        data.expanded = false;
        this.stories.push(data);
        console.log('Current stories:', this.stories);
      },
      error: (err) => {
        console.error('Streaming error:', err);
        this.isLoading = false;
      },
      complete: () => {
        this.isLoading = false;
      }
    });
    this.offset += 10;
  }

  toggleStory(story: any) {
    story.expanded = !story.expanded;
  }
}
