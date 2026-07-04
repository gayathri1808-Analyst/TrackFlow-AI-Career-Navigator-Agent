import sqlite3
from trackflow_career_agent.storage.database import get_connection

def save_user_profile(
    user_id: str,
    degree: str,
    year_of_study: str,
    interests: str,
    goals: str,
    skills: list[str]
) -> str:
    """
    Saves or updates the career profile of a user in the SQLite database.
    
    Args:
        user_id: Unique identifier for the user (e.g. "default").
        degree: The degree or field of study of the user.
        year_of_study: Current year of study (e.g., "1st Year", "Junior", "Graduated").
        interests: Career interests, domains or fields the user wants to work in.
        goals: Short-term or long-term career goals.
        skills: A list of current skills the user already possesses.
        
    Returns:
        A confirmation message indicating successful saving.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Save or update profile
        cursor.execute("""
        INSERT INTO user_profiles (user_id, degree, year_of_study, interests, goals)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            degree=excluded.degree,
            year_of_study=excluded.year_of_study,
            interests=excluded.interests,
            goals=excluded.goals;
        """, (user_id, degree, year_of_study, interests, goals))
        
        # Clear existing skills and insert new ones
        cursor.execute("DELETE FROM user_skills WHERE user_id = ?;", (user_id,))
        for skill in skills:
            if skill.strip():
                cursor.execute("""
                INSERT INTO user_skills (user_id, skill_name)
                VALUES (?, ?);
                """, (user_id, skill.strip()))
                
        conn.commit()
        return f"Successfully saved profile for user: {user_id}"
    except Exception as e:
        conn.rollback()
        return f"Failed to save profile: {e}"
    finally:
        conn.close()

def get_user_profile(user_id: str) -> dict:
    """
    Retrieves the career profile and skills of a user from the SQLite database.
    
    Args:
        user_id: Unique identifier for the user (e.g. "default").
        
    Returns:
        A dictionary containing the profile details (degree, year_of_study, interests, goals, skills).
        If user does not exist, returns a dictionary with empty values.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Fetch profile
        cursor.execute("""
        SELECT degree, year_of_study, interests, goals 
        FROM user_profiles WHERE user_id = ?;
        """, (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return {
                "user_id": user_id,
                "status": "Profile not found",
                "degree": "",
                "year_of_study": "",
                "interests": "",
                "goals": "",
                "skills": []
            }
            
        profile = dict(row)
        
        # Fetch skills
        cursor.execute("SELECT skill_name FROM user_skills WHERE user_id = ?;", (user_id,))
        skills = [r["skill_name"] for r in cursor.fetchall()]
        
        profile["user_id"] = user_id
        profile["skills"] = skills
        profile["status"] = "Found"
        return profile
    except Exception as e:
        return {
            "user_id": user_id,
            "status": f"Error: {e}",
            "degree": "",
            "year_of_study": "",
            "interests": "",
            "goals": "",
            "skills": []
        }
    finally:
        conn.close()

def save_resume_review(
    user_id: str,
    file_path: str,
    parsed_text: str,
    ats_score: int,
    feedback: str
) -> str:
    """
    Saves or updates a user's resume review details in the SQLite database.
    
    Args:
        user_id: Unique identifier for the user (e.g. "default").
        file_path: Absolute or relative path to the parsed resume file.
        parsed_text: The extracted raw text content of the resume.
        ats_score: The calculated ATS suitability score (0-100).
        feedback: Detailed constructive feedback and suggestions for optimization.
        
    Returns:
        A confirmation message indicating successful saving.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Ensure the user exists in user_profiles to satisfy foreign key constraints
        cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?;", (user_id,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO user_profiles (user_id, degree, year_of_study, interests, goals)
            VALUES (?, '', '', '', '');
            """, (user_id,))
            
        cursor.execute("""
        INSERT INTO user_resumes (user_id, file_path, parsed_text, ats_score, feedback)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            file_path=excluded.file_path,
            parsed_text=excluded.parsed_text,
            ats_score=excluded.ats_score,
            feedback=excluded.feedback;
        """, (user_id, file_path, parsed_text, ats_score, feedback))
        
        conn.commit()
        return f"Successfully saved resume review for user: {user_id}"
    except Exception as e:
        conn.rollback()
        return f"Failed to save resume review: {e}"
    finally:
        conn.close()

def get_resume_review(user_id: str) -> dict:
    """
    Retrieves the saved resume review details of a user from the SQLite database.
    
    Args:
        user_id: Unique identifier for the user (e.g. "default").
        
    Returns:
        A dictionary containing the resume review metrics (file_path, parsed_text, ats_score, feedback).
        If no review is found, returns a dictionary with empty/default values.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT file_path, parsed_text, ats_score, feedback 
        FROM user_resumes WHERE user_id = ?;
        """, (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return {
                "user_id": user_id,
                "status": "No review found",
                "file_path": "",
                "parsed_text": "",
                "ats_score": 0,
                "feedback": ""
            }
            
        res = dict(row)
        res["user_id"] = user_id
        res["status"] = "Found"
        return res
    except Exception as e:
        return {
            "user_id": user_id,
            "status": f"Error: {e}",
            "file_path": "",
            "parsed_text": "",
            "ats_score": 0,
            "feedback": ""
        }
    finally:
        conn.close()

def save_skill_gap_analysis(
    user_id: str,
    target_career: str,
    match_percentage: int,
    missing_tech_skills: list[str],
    missing_soft_skills: list[str],
    roadmap: str,
    certifications: list[str],
    projects: list[str],
    timeline: str
) -> str:
    """
    Saves or updates a user's skill gap analysis report in the SQLite database.
    
    Args:
        user_id: Unique identifier for the user (e.g. "default").
        target_career: The user's target career path or target company.
        match_percentage: Calculated skill alignment score (0-100).
        missing_tech_skills: List of technical skills the user needs to acquire.
        missing_soft_skills: List of soft skills the user needs to acquire.
        roadmap: Detailed study roadmap recommendations.
        certifications: Recommended certifications for target role.
        projects: Proposed portfolio project ideas.
        timeline: Expected preparation duration or milestone timeline.
        
    Returns:
        A confirmation message indicating successful saving.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Ensure user exists in user_profiles to satisfy foreign key constraints
        cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?;", (user_id,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO user_profiles (user_id, degree, year_of_study, interests, goals)
            VALUES (?, '', '', '', '');
            """, (user_id,))
            
        # Serialize lists to comma-separated strings
        tech_str = ", ".join(missing_tech_skills)
        soft_str = ", ".join(missing_soft_skills)
        certs_str = ", ".join(certifications)
        projects_str = ", ".join(projects)
        
        cursor.execute("""
        INSERT INTO skill_gap_analyses (
            user_id, target_career, match_percentage, 
            missing_tech_skills, missing_soft_skills, 
            roadmap, certifications, projects, timeline
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            target_career=excluded.target_career,
            match_percentage=excluded.match_percentage,
            missing_tech_skills=excluded.missing_tech_skills,
            missing_soft_skills=excluded.missing_soft_skills,
            roadmap=excluded.roadmap,
            certifications=excluded.certifications,
            projects=excluded.projects,
            timeline=excluded.timeline,
            timestamp=CURRENT_TIMESTAMP;
        """, (
            user_id, target_career, match_percentage, 
            tech_str, soft_str, 
            roadmap, certs_str, projects_str, timeline
        ))
        
        conn.commit()
        return f"Successfully saved skill gap analysis for user: {user_id}"
    except Exception as e:
        conn.rollback()
        return f"Failed to save skill gap analysis: {e}"
    finally:
        conn.close()

def get_skill_gap_analysis(user_id: str) -> dict:
    """
    Retrieves the saved skill gap analysis details of a user from the SQLite database.
    
    Args:
        user_id: Unique identifier for the user (e.g. "default").
        
    Returns:
        A dictionary containing the skill gap analysis (target_career, match_percentage, missing_tech_skills, missing_soft_skills, roadmap, certifications, projects, timeline).
        If no record is found, returns a dictionary with empty/default values.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT target_career, match_percentage, missing_tech_skills, 
               missing_soft_skills, roadmap, certifications, projects, timeline 
        FROM skill_gap_analyses WHERE user_id = ?;
        """, (user_id,))
        row = cursor.fetchone()
        
        if not row:
            return {
                "user_id": user_id,
                "status": "No analysis found",
                "target_career": "",
                "match_percentage": 0,
                "missing_tech_skills": [],
                "missing_soft_skills": [],
                "roadmap": "",
                "certifications": [],
                "projects": [],
                "timeline": ""
            }
            
        res = dict(row)
        # Deserialize strings back to lists
        res["missing_tech_skills"] = [s.strip() for s in res["missing_tech_skills"].split(",")] if res["missing_tech_skills"] else []
        res["missing_soft_skills"] = [s.strip() for s in res["missing_soft_skills"].split(",")] if res["missing_soft_skills"] else []
        res["certifications"] = [s.strip() for s in res["certifications"].split(",")] if res["certifications"] else []
        res["projects"] = [s.strip() for s in res["projects"].split(",")] if res["projects"] else []
        
        res["user_id"] = user_id
        res["status"] = "Found"
        return res
    except Exception as e:
        return {
            "user_id": user_id,
            "status": f"Error: {e}",
            "target_career": "",
            "match_percentage": 0,
            "missing_tech_skills": [],
            "missing_soft_skills": [],
            "roadmap": "",
            "certifications": [],
            "projects": [],
            "timeline": ""
        }
    finally:
        conn.close()

def save_interview_session(
    user_id: str,
    target_role: str,
    question: str,
    user_answer: str,
    technical_score: int,
    communication_score: int,
    confidence_score: int,
    overall_score: int,
    feedback: str
) -> str:
    """
    Saves an interview question, user answer, performance scores, and feedback in SQLite.
    
    Args:
        user_id: Unique identifier for the user (e.g., "default").
        target_role: The role being interviewed for.
        question: The interview question asked.
        user_answer: The user's answer response.
        technical_score: Score for Technical Knowledge (0-100).
        communication_score: Score for Communication (0-100).
        confidence_score: Score for Confidence (0-100).
        overall_score: Overall performance score (0-100).
        feedback: Strengths, weaknesses, and suggestions.
        
    Returns:
        A confirmation message.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Ensure user exists to satisfy foreign keys
        cursor.execute("SELECT user_id FROM user_profiles WHERE user_id = ?;", (user_id,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO user_profiles (user_id, degree, year_of_study, interests, goals)
            VALUES (?, '', '', '', '');
            """, (user_id,))
            
        cursor.execute("""
        INSERT INTO interview_sessions (
            user_id, target_role, question, user_answer, 
            technical_score, communication_score, confidence_score, 
            overall_score, feedback
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            user_id, target_role, question, user_answer, 
            technical_score, communication_score, confidence_score, 
            overall_score, feedback
        ))
        
        conn.commit()
        return f"Successfully saved interview session record for user: {user_id}"
    except Exception as e:
        conn.rollback()
        return f"Failed to save interview session: {e}"
    finally:
        conn.close()

def get_interview_history(user_id: str) -> list[dict]:
    """
    Retrieves the complete mock interview QA history for a user from SQLite.
    
    Args:
        user_id: Unique identifier for the user (e.g. "default").
        
    Returns:
        A list of dictionaries representing previous interview QA turns.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, target_role, question, user_answer, technical_score, 
               communication_score, confidence_score, overall_score, feedback, timestamp 
        FROM interview_sessions WHERE user_id = ?
        ORDER BY timestamp ASC;
        """, (user_id,))
        rows = cursor.fetchall()
        
        history = [dict(row) for row in rows]
        return history
    except Exception as e:
        print(f"Error fetching interview history: {e}")
        return []
    finally:
        conn.close()



