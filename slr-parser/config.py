import os 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "Compiler-2025-project-sk"
    TEMPLATES_AUTO_RELOAD = True