/**
 * Interface representing a Hacker News story with its associated data.
 * 
 * This interface defines the structure for stories fetched from the Hacker News API
 * and includes additional fields for the application's features like screenshots
 * and AI analysis.
 */
export interface Story {
  /** Unique identifier for the story on Hacker News */
  hn_id: string;
  /** Title of the story */
  title: string;
  /** URL to the Hacker News discussion page */
  url: string;
  /** URL to the original article */
  article_url: string;
  /** Number of upvotes/points the story has received */
  points: number;
  /** Username of the story author */
  author: string;
  /** Total number of comments on the story */
  comments_count: number;
  /** Unix timestamp of when the story was posted */
  time: number;
  /** HTML content of the full article (optional) */
  full_article_html?: string;
  /** Metadata about the article (optional) */
  article_metadata?: any;
  /** Path to the article screenshot (optional) */
  screenshot_path?: string;
  /** Error message if screenshot failed (optional) */
  screenshot_error?: string;
  /** AI-generated hook/summary of the article (optional) */
  hook?: string;
  /** Array of top comments on the story (optional) */
  top_comments?: Comment[];
  /** AI analysis of the article content (optional) */
  analysis?: any;
  /** Flag indicating if more content is available (optional) */
  has_more?: boolean;
  /** UI state for expanded view (optional) */
  expanded?: boolean;
  /** UI state for article visibility (optional) */
  showArticle?: boolean;
  /** UI state for comments visibility (optional) */
  showComments?: boolean;
}

/**
 * Interface representing a comment on a Hacker News story.
 * 
 * This interface defines the structure for comments, including nested replies
 * through the children property.
 */
export interface Comment {
  /** Unique identifier for the comment */
  id: string;
  /** Username of the comment author */
  author: string;
  /** HTML content of the comment */
  text: string;
  /** Unix timestamp of when the comment was posted */
  time: number;
  /** Nesting level of the comment (0 for top-level) */
  depth: number;
  /** Array of nested replies (optional) */
  children?: Comment[];
} 