import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def analyze_article(article_html, comments):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the prompt
        prompt = f"""
        Analyze this article and its comments. Provide:
        1. A brief summary of the article
        2. Key points discussed in the comments
        3. Overall sentiment of the discussion
        
        Article content:
        {article_html}
        
        Comments:
        {comments}
        """
        
        # Generate analysis
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing content: {str(e)}"
