"""
Configuration file for NESCO Resourcing Agent
Easily modify API keys and model settings here
"""

# Google Gemini API Configuration
GEMINI_API_KEY = "AIzaSyAd-tF96iklh3IwOzOQrLrWcJdXYGn_AyA"
GEMINI_MODEL_NAME = "gemini-flash-latest"

# Alternative models you can use:
# - "gemini-2.0-flash-lite"
# - "gemini-2.5-flash-preview-09-2025"
# - "gemini-pro-latest"
# - "gemini-2.0-pro-exp"

# File paths (optional - can be overridden by command line args)
DEFAULT_SURGE_DATA = "data/mumbai_hospitals_surge_categories.csv"
DEFAULT_INVENTORY = "Hsupply.json"
DEFAULT_OUTPUT = "mumbai_enhanced_report.json"
