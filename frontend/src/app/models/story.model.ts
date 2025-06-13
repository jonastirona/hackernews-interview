export interface Story {
  title: string;
  article_url: string;
  author: string;
  points: number;
  full_article_html?: string;
  top_comments: Array<{
    user: string;
    comment: string;
  }>;
  expanded: boolean;
  showArticle: boolean;
  showComments: boolean;
} 