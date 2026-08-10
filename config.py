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
