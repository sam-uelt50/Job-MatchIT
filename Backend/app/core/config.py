import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Application
    PROJECT_NAME: str = "AI Recruitment System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # MongoDB Atlas
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://samueltesema56_db_user:Shmuel52%25100@cluster0.4dfoa3f.mongodb.net/?appName=Cluster0")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "recruitment_db")
    MONGODB_MAX_POOL_SIZE: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "50"))
    MONGODB_MIN_POOL_SIZE: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "jwt-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
    ALLOWED_EXTENSIONS_STR: str = os.getenv("ALLOWED_EXTENSIONS", ".pdf,.docx,.doc,.txt")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "temp")
    
    @property
    def ALLOWED_EXTENSIONS(self):
        return set(self.ALLOWED_EXTENSIONS_STR.split(","))
    
    # AI/ML Models
    SPACY_MODEL: str = os.getenv("SPACY_MODEL", "en_core_web_lg")
    
    # CORS
    CORS_ORIGINS_STR: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    
    @property
    def CORS_ORIGINS(self):
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
    
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    
    # Matching Weights
    SKILL_WEIGHT: float = float(os.getenv("SKILL_WEIGHT", "0.40"))
    EXPERIENCE_WEIGHT: float = float(os.getenv("EXPERIENCE_WEIGHT", "0.25"))
    EDUCATION_WEIGHT: float = float(os.getenv("EDUCATION_WEIGHT", "0.15"))
    SEMANTIC_WEIGHT: float = float(os.getenv("SEMANTIC_WEIGHT", "0.20"))
    
    # Thresholds
    STRONG_FIT_THRESHOLD: float = float(os.getenv("STRONG_FIT_THRESHOLD", "85"))
    MODERATE_FIT_THRESHOLD: float = float(os.getenv("MODERATE_FIT_THRESHOLD", "60"))
    
    # Recommendations
    MAX_RECOMMENDATIONS: int = int(os.getenv("MAX_RECOMMENDATIONS", "20"))
    CONTENT_BASED_WEIGHT: float = float(os.getenv("CONTENT_BASED_WEIGHT", "0.7"))
    COLLABORATIVE_FILTERING_WEIGHT: float = float(os.getenv("COLLABORATIVE_FILTERING_WEIGHT", "0.3"))

settings = Settings()
