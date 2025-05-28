
# backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import re
from datetime import datetime
from enum import Enum
import httpx
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Aayush's Portfolio API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Complete bio context for DeepSeek
AAYUSH_CONTEXT = """
I am Aayush Kushwaha, a passionate backend developer with 2 years 9 months of experience building efficient and scalable systems.

Current Role: Software Engineer at DigitalPetro Private Limited (Sep 2022 - Present) in Bengaluru, Karnataka, India.

Key Achievements:
- Reduced API response time from 45 seconds to <1 second through optimization
- Spearheaded IoT systems development for petrol stations
- Implemented high-performance Redis caching solutions
- Built scalable systems using FastAPI, Redis, and RabbitMQ

Technical Skills:
- Languages: Python (Expert)
- Frameworks: FastAPI, Django
- Databases: Redis, PostgreSQL, MongoDB
- Message Brokers: RabbitMQ
- Search: Elasticsearch
- Tools: Docker, Git
- Specialization: Backend development, IoT systems, API optimization

Previous Experience:
1. Student Mentor at JSpiders (Jul 2022 - Sep 2022): Mentored 200+ students on Python and career development
2. Engineer Intern at DigiNirman (Aug 2021 - Jun 2022): Developed AI Robo Traffic project scripts

Education: Bachelor of Technology in Computer Science and Engineering

I'm passionate about creating efficient backend solutions and always eager to tackle challenging problems.
"""

DEEPSEEK_API_KEY = "sk-c8fd68accffc4adc8b3b7dc12a22abcf"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_llm_only: Optional[bool] = False  # Force LLM response

class ChatResponse(BaseModel):
    response: str
    session_id: str
    source: str  # Shows whether response came from structured data or LLM

class QueryRequest(BaseModel):
    query: str
    category: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    source: str

class UpdateRequest(BaseModel):
    category: str
    field: str
    value: str

# Structured Profile Database
class ProfileDatabase:
    def __init__(self):
        self.data = {
            "personal": {
                "name": "Aayush Kushwaha",
                "title": "Backend Developer",
                "location": "Bengaluru, Karnataka, India",
                "email": "aayush@example.com",  # Add your actual email
                "linkedin": "linkedin.com/in/aayush-kushwaha",  # Add your actual LinkedIn
                "github": "github.com/aayush",  # Add your actual GitHub
                "summary": "A passionate backend developer with a strong drive for building efficient and scalable systems. Experienced in optimizing APIs, implementing caching solutions, and developing IoT systems."
            },
            "skills": {
                "primary": ["Python", "FastAPI", "Redis", "RabbitMQ", "Elasticsearch"],
                "frameworks": ["FastAPI", "Django"],
                "databases": ["Redis", "PostgreSQL", "MongoDB"],
                "tools": ["Docker", "Git", "RabbitMQ"],
                "specialization": "Backend development, IoT systems, API optimization",
                "proficiency": {
                    "Python": "Expert",
                    "FastAPI": "Advanced",
                    "Redis": "Advanced",
                    "PostgreSQL": "Intermediate",
                    "Docker": "Intermediate"
                }
            },
            "experience": {
                "total_years": "2 years 9 months",
                "current": {
                    "company": "DigitalPetro Private Limited",
                    "role": "Software Engineer",
                    "duration": "Sep 2022 - Present",
                    "location": "Bengaluru, Karnataka, India",
                    "type": "Full-time",
                    "responsibilities": [
                        "Develop and maintain backend services for IoT-enabled petrol stations",
                        "Design and implement RESTful APIs using FastAPI",
                        "Optimize database queries and implement caching strategies",
                        "Integrate with message brokers for asynchronous processing"
                    ],
                    "achievements": [
                        "Spearheaded IoT systems development in petrol stations",
                        "Reduced API response time from 45 seconds to <1 second",
                        "Implemented Redis caching for high-performance solutions",
                        "Leveraged FastAPI, Redis, and RabbitMQ for scalable architecture"
                    ],
                    "technologies": ["Python", "FastAPI", "Redis", "RabbitMQ", "PostgreSQL", "Docker"]
                },
                "previous": [
                    {
                        "company": "JSpiders - Training & Development Center",
                        "role": "Student Mentor",
                        "duration": "Jul 2022 - Sep 2022",
                        "period": "3 months",
                        "location": "Bengaluru, Karnataka, India",
                        "type": "Part-time",
                        "responsibilities": [
                            "Mentor students on Python programming and databases",
                            "Conduct mock interviews and career counseling",
                            "Develop curriculum for backend development courses"
                        ],
                        "achievements": [
                            "Mentored 200+ students on career goals",
                            "Provided Python and database guidance",
                            "Conducted mock interviews with 90% student satisfaction"
                        ]
                    },
                    {
                        "company": "DigiNirman",
                        "role": "Engineer Intern",
                        "duration": "Aug 2021 - Jun 2022",
                        "period": "11 months",
                        "location": "Biratnagar, Nepal",
                        "type": "Full-time",
                        "responsibilities": [
                            "Develop automation scripts for AI projects",
                            "Annotate and process video data using CVAT",
                            "Build CRUD applications for data management"
                        ],
                        "achievements": [
                            "Developed scripts for AI Robo Traffic project",
                            "Utilized CVAT for video data annotation",
                            "Built CRUD operation project with 95% accuracy in data processing"
                        ]
                    }
                ]
            },
            "education": {
                "degree": "Bachelor of Technology",
                "field": "Computer Science and Engineering",
                "graduation_year": "2022",
                "coursework": ["Data Structures", "Algorithms", "Database Management", "Software Engineering"]
            },
            "achievements": {
                "performance": "Reduced API load times from 45 seconds to less than 1 second",
                "scale": "Mentored 200+ students successfully",
                "technical": "Implemented efficient Redis caching system reducing database load by 80%",
                "recognition": "Recognized for exceptional performance in IoT project delivery"
            },
            "projects": {
                "iot_petrol_station": {
                    "name": "IoT-Enabled Petrol Station Management",
                    "description": "Developed backend for managing IoT devices in petrol stations",
                    "technologies": ["FastAPI", "Redis", "RabbitMQ", "PostgreSQL"],
                    "impact": "Improved operational efficiency by 40%"
                },
                "api_optimization": {
                    "name": "API Performance Optimization",
                    "description": "Optimized legacy APIs reducing response time from 45s to <1s",
                    "technologies": ["Python", "Redis", "Elasticsearch"],
                    "impact": "Enhanced user experience for 10,000+ daily users"
                }
            }
        }

        # Enhanced keyword mappings
        self.keyword_map = {
            # Skills keywords
            "python": ["skills", "primary"],
            "fastapi": ["skills", "frameworks"],
            "redis": ["skills", "databases"],
            "backend": ["personal", "title"],
            "docker": ["skills", "tools"],
            "postgresql": ["skills", "databases"],
            "mongodb": ["skills", "databases"],
            "rabbitmq": ["skills", "tools"],
            
            # Experience keywords
            "experience": ["experience", "total_years"],
            "current job": ["experience", "current"],
            "digitalpetro": ["experience", "current"],
            "jspiders": ["experience", "previous", 0],
            "diginirman": ["experience", "previous", 1],
            "responsibilities": ["experience", "current", "responsibilities"],
            
            # Achievement keywords
            "achievement": ["achievements"],
            "performance": ["achievements", "performance"],
            "api optimization": ["achievements", "performance"],
            "mentoring": ["achievements", "scale"],
            
            # Location keywords
            "location": ["personal", "location"],
            "bengaluru": ["personal", "location"],
            "bangalore": ["personal", "location"],
            "nepal": ["experience", "previous", 1, "location"],
            
            # Education keywords
            "education": ["education"],
            "degree": ["education", "degree"],
            "graduation": ["education", "graduation_year"],
            
            # Project keywords
            "projects": ["projects"],
            "iot": ["projects", "iot_petrol_station"],
            "api": ["projects", "api_optimization"],
            
            # Contact keywords
            "contact": ["personal"],
            "email": ["personal", "email"],
            "linkedin": ["personal", "linkedin"],
            "github": ["personal", "github"]
        }

    def get(self, path: List[str]):
        """Navigate through nested dictionary using path"""
        result = self.data
        try:
            for key in path:
                if isinstance(result, list):
                    result = result[int(key)]
                else:
                    result = result[key]
            return result
        except (KeyError, IndexError, ValueError):
            return None

    def update(self, category: str, field: str, value: str) -> bool:
        """Update a specific field (CRUD Update operation)"""
        if category in self.data and field in self.data[category]:
            self.data[category][field] = value
            logger.info(f"Updated {category}.{field} to {value}")
            return True
        return False

    def search_by_keyword(self, keyword: str):
        """Quick keyword-based search"""
        keyword_lower = keyword.lower()
        if keyword_lower in self.keyword_map:
            path = self.keyword_map[keyword_lower]
            return self.get(path)
        return None

    def add_skill(self, skill: str, category: str = "primary") -> bool:
        """Add a new skill to the profile"""
        if category in self.data["skills"] and isinstance(self.data["skills"][category], list):
            if skill not in self.data["skills"][category]:
                self.data["skills"][category].append(skill)
                logger.info(f"Added skill: {skill} to {category}")
                return True
        return False

# Enhanced Pattern Matcher
class QueryProcessor:
    def __init__(self, db: ProfileDatabase):
        self.db = db
        # Enhanced query patterns
        self.patterns = {
            "skills": r"(skill|technology|tech|stack|know|expert|proficient|language|framework|database|tool)",
            "experience": r"(experience|work|job|year|duration|career|employment)",
            "company": r"(company|organization|work at|employer|firm)",
            "achievement": r"(achieve|accomplish|success|improve|reduce|impact|result)",
            "location": r"(location|where|place|city|country|based|live)",
            "current": r"(current|now|present|today|ongoing)",
            "previous": r"(previous|past|before|earlier|former)",
            "education": r"(education|degree|study|university|college|graduation)",
            "project": r"(project|built|developed|created|worked on)",
            "contact": r"(contact|email|linkedin|github|reach|connect)",
            "responsibility": r"(responsibility|duties|role|task|work on)"
        }

    def process_query(self, query: str) -> Dict[str, any]:
        query_lower = query.lower()
        
        # Check for skills queries
        if re.search(self.patterns["skills"], query_lower):
            skills = self.db.get(["skills", "primary"])
            frameworks = self.db.get(["skills", "frameworks"])
            databases = self.db.get(["skills", "databases"])
            specialization = self.db.get(["skills", "specialization"])
            
            # Check for specific skill proficiency
            for skill in skills + frameworks + databases:
                if skill.lower() in query_lower:
                    proficiency = self.db.get(["skills", "proficiency", skill])
                    if proficiency:
                        return {
                            "answer": f"Proficiency in {skill}: {proficiency}",
                            "confidence": 0.95,
                            "source": "skills_proficiency"
                        }
            
            return {
                "answer": f"Technical skills include:\n- Languages: {', '.join(skills)}\n- Frameworks: {', '.join(frameworks)}\n- Databases: {', '.join(databases)}\n- Specialization: {specialization}",
                "confidence": 0.95,
                "source": "skills_database"
            }

        # Check for experience queries
        if re.search(self.patterns["experience"], query_lower):
            if re.search(self.patterns["current"], query_lower):
                current = self.db.get(["experience", "current"])
                achievements = '\n- '.join(current['achievements'])
                return {
                    "answer": f"Currently working as {current['role']} at {current['company']} since {current['duration'].split('-')[0].strip()}.\n\nKey achievements:\n- {achievements}",
                    "confidence": 0.95,
                    "source": "experience_current"
                }
            elif re.search(self.patterns["responsibility"], query_lower):
                responsibilities = self.db.get(["experience", "current", "responsibilities"])
                resp_list = '\n- '.join(responsibilities)
                return {
                    "answer": f"Current responsibilities:\n- {resp_list}",
                    "confidence": 0.90,
                    "source": "responsibilities"
                }
            else:
                total = self.db.get(["experience", "total_years"])
                return {
                    "answer": f"Total professional experience: {total}",
                    "confidence": 0.90,
                    "source": "experience_total"
                }

        # Check for education queries
        if re.search(self.patterns["education"], query_lower):
            education = self.db.get(["education"])
            return {
                "answer": f"Education: {education['degree']} in {education['field']}, graduated in {education['graduation_year']}",
                "confidence": 0.95,
                "source": "education"
            }

        # Check for project queries
        if re.search(self.patterns["project"], query_lower):
            projects = self.db.get(["projects"])
            project_info = []
            for key, project in projects.items():
                project_info.append(f"- {project['name']}: {project['description']} (Impact: {project['impact']})")
            return {
                "answer": f"Key projects:\n" + '\n'.join(project_info),
                "confidence": 0.90,
                "source": "projects"
            }

        # Check for contact queries
        if re.search(self.patterns["contact"], query_lower):
            contact = self.db.get(["personal"])
            return {
                "answer": f"Contact information:\n- Email: {contact.get('email', 'Not provided')}\n- LinkedIn: {contact.get('linkedin', 'Not provided')}\n- GitHub: {contact.get('github', 'Not provided')}",
                "confidence": 0.95,
                "source": "contact_info"
            }

        # Check for achievement queries
        if re.search(self.patterns["achievement"], query_lower):
            achievements = self.db.get(["achievements"])
            ach_list = []
            for key, value in achievements.items():
                ach_list.append(f"- {key.title()}: {value}")
            return {
                "answer": f"Key achievements:\n" + '\n'.join(ach_list),
                "confidence": 0.90,
                "source": "achievements"
            }

        # Try keyword search as fallback
        words = query_lower.split()
        for word in words:
            result = self.db.search_by_keyword(word)
            if result:
                return {
                    "answer": f"Found information: {json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)}",
                    "confidence": 0.70,
                    "source": "keyword_search"
                }

        return {
            "answer": "I couldn't find specific information about that in the structured data. Let me search with AI...",
            "confidence": 0.0,
            "source": "no_match"
        }

# Initialize database and processor
profile_db = ProfileDatabase()
query_processor = QueryProcessor(profile_db)

# DeepSeek API integration
async def query_deepseek(user_message: str):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": f"You are Aayush's AI assistant. Respond as if you are Aayush himself. Here's context about Aayush: {AAYUSH_CONTEXT}"
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    timeout = httpx.Timeout(
        connect=5.0,
        read=30.0,
        write=5.0,
        pool=5.0
    )
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from DeepSeek: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error calling DeepSeek API: {str(e)}")
        raise

# Enhanced chat endpoint with hybrid approach
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Hybrid chat endpoint that tries structured data first, then falls back to LLM
    """
    try:
        # If user specifically wants LLM response
        if request.use_llm_only:
            result = await query_deepseek(request.message)
            return ChatResponse(
                response=result["choices"][0]["message"]["content"],
                session_id=request.session_id or "default",
                source="deepseek_llm"
            )
        
        # Try structured data first
        structured_result = query_processor.process_query(request.message)
        
        # If we have a confident match from structured data
        if structured_result["confidence"] > 0.7:
            return ChatResponse(
                response=structured_result["answer"],
                session_id=request.session_id or "default",
                source=structured_result["source"]
            )
        
        # Otherwise, use LLM for more natural response
        llm_result = await query_deepseek(request.message)
        return ChatResponse(
            response=llm_result["choices"][0]["message"]["content"],
            session_id=request.session_id or "default",
            source="deepseek_llm_fallback"
        )
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        # Final fallback to structured data
        fallback_result = query_processor.process_query(request.message)
        return ChatResponse(
            response=fallback_result["answer"] if fallback_result["answer"] else "I'm having trouble processing your request. Please try asking about my skills, experience, or projects.",
            session_id=request.session_id or "default",
            source="error_fallback"
        )

# Query endpoint (structured data only)
@app.post("/query", response_model=QueryResponse)
async def query_profile(request: QueryRequest):
    """Query endpoint using only structured data"""
    result = query_processor.process_query(request.query)
    return QueryResponse(**result)

# CRUD Endpoints
@app.get("/profile/{category}")
async def get_profile_category(category: str):
    """Get specific category data"""
    if category in profile_db.data:
        return profile_db.data[category]
    raise HTTPException(status_code=404, detail=f"Category '{category}' not found")

@app.get("/profile")
async def get_full_profile():
    """Get complete profile"""
    return profile_db.data

@app.put("/profile/update")
async def update_profile(request: UpdateRequest):
    """Update profile field"""
    success = profile_db.update(request.category, request.field, request.value)
    if success:
        return {"message": "Profile updated successfully", "updated": {request.field: request.value}}
    raise HTTPException(status_code=400, detail="Invalid category or field")

@app.post("/skills/add")
async def add_skill(skill: str, category: str = "primary"):
    """Add a new skill"""
    success = profile_db.add_skill(skill, category)
    if success:
        return {"message": f"Skill '{skill}' added successfully"}
    return {"message": f"Skill '{skill}' already exists or invalid category"}

@app.get("/search/{keyword}")
async def search_keyword(keyword: str):
    """Quick keyword search"""
    result = profile_db.search_by_keyword(keyword)
    if result:
        return {"keyword": keyword, "result": result}
    
    # Try LLM for keywords not in structured data
    try:
        llm_result = await query_deepseek(f"Tell me about {keyword}")
        return {
            "keyword": keyword, 
            "result": llm_result["choices"][0]["message"]["content"],
            "source": "deepseek_llm"
        }
    except:
        raise HTTPException(status_code=404, detail=f"No information found for '{keyword}'")

# Analytics endpoints
@app.get("/analytics/skills-count")
async def get_skills_count():
    """Get count of skills by category"""
    skills = profile_db.data["skills"]
    return {
        "primary": len(skills.get("primary", [])),
        "frameworks": len(skills.get("frameworks", [])),
        "databases": len(skills.get("databases", [])),
        "tools": len(skills.get("tools", []))
    }

@app.get("/analytics/experience-timeline")
async def get_experience_timeline():
    """Get experience timeline"""
    timeline = []
    current = profile_db.data["experience"]["current"]
    timeline.append({
        "company": current["company"],
        "role": current["role"],
        "period": current["duration"],
        "current": True
    })
    
    for prev in profile_db.data["experience"]["previous"]:
        timeline.append({
            "company": prev["company"],
            "role": prev["role"],
            "period": prev["duration"],
            "current": False
        })
    
    return {"timeline": timeline}

# Example queries endpoint
@app.get("/examples")
async def get_example_queries():
    """Provide example queries for testing"""
    return {
        "structured_queries": [
            "What are your technical skills?",
            "Tell me about your current job",
            "Which companies have you worked at?",
            "What is your biggest achievement?",
            "Where are you located?",
            "How many years of experience do you have?",
            "What projects have you worked on?",
            "What is your education background?",
            "How can I contact you?"
        ],
        "llm_queries": [
            "What makes you passionate about backend development?",
            "How do you approach solving complex problems?",
            "What are your career goals?",
            "Tell me about a challenging project you've worked on",
            "Why did you choose to work with FastAPI?",
            "What's your experience with microservices?"
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "api": "Aayush's Portfolio API",
        "version": "1.0.0",
        "structured_data": "active",
        "llm_integration": "active"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Aayush's Portfolio API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

