# API Endpoints
BACKEND_URL = "http://localhost:8000" 
MODEL_API_BASE = f"{BACKEND_URL}/api/v1"
USER_API_BASE = f"{BACKEND_URL}/users"

# App configuration
APP_NAME = "GDP Shock Predictor"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Predict GDP shocks using macroeconomic indicators"

# Session state keys
SESSION_USER = "user"
SESSION_TOKEN = "token"
SESSION_CHAT_HISTORY = "chat_history"

# Pagination
ITEMS_PER_PAGE = 10

# File upload types
ALLOWED_EXTENSIONS = ["csv"]
MAX_FILE_SIZE_MB = 10

# Region options (based on World Bank regions)
REGIONS = [
    "East Asia & Pacific",
    "Europe & Central Asia",
    "Latin America & Caribbean",
    "Middle East & North Africa",
    "North America",
    "South Asia",
    "Sub-Saharan Africa"
]

# Income groups
INCOME_GROUPS = [
    "Low income",
    "Lower middle income",
    "Upper middle income",
    "High income"
]

# Lending types
LENDING_TYPES = [
    "IBRD",
    "IDA",
    "Blend",
    "Not classified"
]

# Crisis decades
CRISIS_DECADES = ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]