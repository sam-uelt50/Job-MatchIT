# Create constants.py file
@"
"""
Constants Module
Defines all constants used throughout the application
"""

from enum import Enum

# ==================== ENUMS ====================

class UserRole(str, Enum):
    """User role enumeration"""
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    APPLIED = "applied"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class MatchCategory(str, Enum):
    """Match category enumeration"""
    STRONG_FIT = "Strong Fit"
    MODERATE_FIT = "Moderate Fit"
    WEAK_FIT = "Weak Fit"

class EmploymentType(str, Enum):
    """Employment type enumeration"""
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"
    HYBRID = "hybrid"

class ExperienceLevel(str, Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"

class SkillCategory(str, Enum):
    """Skill category enumeration"""
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    CERTIFICATION = "certification"

# ==================== VALIDATION CONSTANTS ====================

# Password validation
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Username validation
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50

# File validation
VALID_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".rtf"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Text validation
MAX_TITLE_LENGTH = 200
MAX_COMPANY_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 10000

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds

# Cache
CACHE_TTL = 300  # 5 minutes
RECOMMENDATION_CACHE_TTL = 3600  # 1 hour

# ==================== SUPPORTED LANGUAGES ====================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean"
}

# ==================== SKILL CATEGORIES ====================

SKILL_CATEGORIES = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "matlab"
    ],
    "web": [
        "react", "angular", "vue", "node.js", "django", "flask", "spring",
        "html", "css", "tailwind", "bootstrap", "jquery"
    ],
    "database": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "oracle", "sqlite", "cassandra", "dynamodb"
    ],
    "cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
        "ci/cd", "devops", "serverless"
    ],
    "data_science": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy"
    ]
}

# ==================== JOB CATEGORIES ====================

JOB_CATEGORIES = [
    "Software Development",
    "Data Science",
    "Machine Learning",
    "DevOps",
    "Cloud Computing",
    "Cybersecurity",
    "Product Management",
    "Project Management",
    "Marketing",
    "Sales",
    "Human Resources",
    "Finance",
    "Operations",
    "Customer Support"
]

# ==================== LOCATIONS ====================

LOCATIONS = [
    "Remote",
    "Hybrid",
    "On-site",
    "United States",
    "Canada",
    "United Kingdom",
    "Germany",
    "France",
    "Australia",
    "India",
    "Singapore",
    "Japan",
    "China"
]

# ==================== SALARY RANGES ====================

SALARY_RANGES = {
    "entry": {"min": 40000, "max": 70000},
    "junior": {"min": 60000, "max": 90000},
    "mid": {"min": 80000, "max": 120000},
    "senior": {"min": 100000, "max": 160000},
    "lead": {"min": 120000, "max": 200000},
    "executive": {"min": 150000, "max": 300000}
}

# ==================== MATCHING WEIGHTS ====================

MATCHING_WEIGHTS = {
    "skill_match": 0.40,
    "experience_match": 0.25,
    "education_match": 0.15,
    "semantic_match": 0.15,
    "certification_match": 0.05
}

# ==================== SCORE THRESHOLDS ====================

SCORE_THRESHOLDS = {
    "strong_fit": 85,
    "moderate_fit": 60,
    "weak_fit": 0
}

# ==================== API MESSAGES ====================

API_MESSAGES = {
    "success": "Operation completed successfully",
    "created": "Resource created successfully",
    "updated": "Resource updated successfully",
    "deleted": "Resource deleted successfully",
    "not_found": "Resource not found",
    "unauthorized": "Unauthorized access",
    "forbidden": "Access forbidden",
    "validation_error": "Validation error",
    "server_error": "Internal server error"
}
"@ | Out-File -FilePath "app\core\constants.py" -Encoding UTF8