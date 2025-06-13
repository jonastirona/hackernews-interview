export interface Story {
  hn_id: string;
  title: string;
  url: string;
  article_url: string;
  points: number;
  author: string;
  comments_count: number;
  full_article_html?: string;
  article_metadata?: any;
  top_comments?: {
    author: string;
    text: string;
    points: number;
    depth: number;
  }[];
  analysis?: string;
  hook?: string;
  expanded?: boolean;
  showArticle?: boolean;
  showComments?: boolean;
  screenshot_path?: string;
} 