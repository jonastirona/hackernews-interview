export interface Story {
  hn_id: string;
  title: string;
  url: string;
  article_url: string;
  points: number;
  author: string;
  comments_count: number;
  time: number;
  full_article_html?: string;
  article_metadata?: any;
  screenshot_path?: string;
  screenshot_error?: string;
  hook?: string;
  top_comments?: Comment[];
  analysis?: any;
  has_more?: boolean;
  expanded?: boolean;
  showArticle?: boolean;
  showComments?: boolean;
}

export interface Comment {
  id: string;
  author: string;
  text: string;
  time: number;
  depth: number;
  children?: Comment[];
} 