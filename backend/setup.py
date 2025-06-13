"""Package setup for Hacker News article analysis backend.

This package provides a FastAPI backend for analyzing Hacker News articles,
generating AI summaries, and taking screenshots of articles.
"""

from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "playwright",
        "beautifulsoup4",
        "google-generativeai",
        "python-dotenv",
    ],
    python_requires=">=3.8",
) 