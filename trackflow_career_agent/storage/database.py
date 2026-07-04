import os
import sqlite3
from trackflow_career_agent.config import DB_PATH

def get_connection():
    """Returns a SQLite connection to the configured DB path, enabling foreign keys."""
    # Ensure storage folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes the SQLite database schema if tables do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create user_profiles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id TEXT PRIMARY KEY,
        degree TEXT,
        year_of_study TEXT,
        interests TEXT,
        goals TEXT
    );
    """)
    
    # Create user_skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        skill_name TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
    );
    """)
    
    # Create user_resumes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_resumes (
        user_id TEXT PRIMARY KEY,
        file_path TEXT,
        parsed_text TEXT,
        ats_score INTEGER,
        feedback TEXT,
        FOREIGN KEY(user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
    );
    """)
    
    # Create skill_gap_analyses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_gap_analyses (
        user_id TEXT PRIMARY KEY,
        target_career TEXT,
        match_percentage INTEGER,
        missing_tech_skills TEXT,
        missing_soft_skills TEXT,
        roadmap TEXT,
        certifications TEXT,
        projects TEXT,
        timeline TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
    );
    """)
    
    # Create interview_sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        target_role TEXT,
        question TEXT,
        user_answer TEXT,
        technical_score INTEGER,
        communication_score INTEGER,
        confidence_score INTEGER,
        overall_score INTEGER,
        feedback TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES user_profiles(user_id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()
