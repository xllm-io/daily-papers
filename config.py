'''
DailyArXiv Configuration
All configurable parameters are defined here.
'''

# Keywords to search on arXiv
# keywords = ["DINO", "Face Recognition", "Face Alignment", "Object Detection", "SAM"]
keywords = ["KV Cache", "Sparse Attention", "Training", "Inference", "Serving", "Quantization", "RL", "Diffusion", "DIT", "MOE", "VLA", "World Model", "video generation"]

# Maximum query results from arXiv API for each keyword
max_result = 50

# Maximum papers to be included in the issue
issues_result = 20

# Output file names
readme_file = "README.md"
issue_template_file = ".github/ISSUE_TEMPLATE.md"

# Column names to display
column_names = ["Title", "Link", "Abstract", "Date", "Comment"]

# Comment length limits
MAX_COMMENT_LENGTH = 500
COMMENT_SUMMARY_LENGTH = 50

# ArXiv API rate-limit delay between keyword queries (seconds)
API_DELAY = 5

# Retry config
MAX_RETRIES = 6
RETRY_DELAY = 60  # seconds
