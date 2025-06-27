from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, date, time
import logging
import pytz

from app.database import get_db, create_tables, init_db
from app.scheduler import CommunicationScheduler
from app.ai_agent import AICommunicationAgent
from app.models import SocialMediaPosts, SocialMediaComments, EventDetails, AIResponses

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Communication Specialist",
    description="Intelligent social media content creation, scheduling, and interaction management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
scheduler = CommunicationScheduler()
ai_agent = AICommunicationAgent()

# Pydantic models for API requests/responses
class SchedulePostRequest(BaseModel):
    prompt: str
    platforms: Optional[List[str]] = ["devto"]  # Only Dev.to for now

class SchedulePostResponse(BaseModel):
    success: bool
    scheduled_posts: Dict[str, Any]
    event: Dict[str, Any]
    error: Optional[str] = None

class PostInfo(BaseModel):
    post_id: str
    platform: str
    scheduled_time: str
    content_preview: str
    campaign_tag: str
    event_title: Optional[str]

class CommentInfo(BaseModel):
    comment_id: str
    post_id: str
    platform: str
    user_name: str
    comment_text: str
    classification: Optional[str]
    timestamp: str

class EventInfo(BaseModel):
    event_id: str
    title: str
    date: str
    time: str
    description: str
    registration_link: Optional[str]
    is_recorded: str

class AIResponseInfo(BaseModel):
    response_id: str
    trigger_type: str
    keyword_match: Optional[str]
    response_text: str

# IST (Asia/Kolkata) timezone
IST = pytz.timezone('Asia/Kolkata')

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    try:
        # Create database tables
        create_tables()
        
        # Initialize with sample data
        init_db()
        
        logger.info("AI Communication Specialist started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        scheduler.shutdown()
        logger.info("AI Communication Specialist shutdown successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Communication Specialist API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/schedule-post", response_model=SchedulePostResponse)
async def schedule_post(request: SchedulePostRequest, db: Session = Depends(get_db)):
    """Schedule social media posts based on natural language prompt"""
    try:
        result = scheduler.schedule_post(request.prompt, request.platforms)
        
        if result["success"]:
            return SchedulePostResponse(
                success=True,
                scheduled_posts=result["scheduled_posts"],
                event=result["event"]
            )
        else:
            return SchedulePostResponse(
                success=False,
                error=result["error"]
            )
    except Exception as e:
        logger.error(f"Error in schedule_post endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheduled-posts", response_model=List[PostInfo])
async def get_scheduled_posts(db: Session = Depends(get_db)):
    """Get all scheduled posts"""
    try:
        posts = scheduler.get_scheduled_posts()
        # Convert scheduled_time to IST for all posts
        for post in posts:
            # If scheduled_time is a string, try to parse and convert
            try:
                dt = datetime.strptime(post['scheduled_time'].split(' ')[0] + ' ' + post['scheduled_time'].split(' ')[1], "%Y-%m-%d %H:%M:%S")
                post['scheduled_time'] = IST.localize(dt).strftime("%Y-%m-%d %H:%M:%S %Z%z")
            except Exception:
                pass
        return [PostInfo(**post) for post in posts]
    except Exception as e:
        logger.error(f"Error getting scheduled posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pending-comments", response_model=List[CommentInfo])
async def get_pending_comments(db: Session = Depends(get_db)):
    """Get all pending comments that need human review"""
    try:
        comments = scheduler.get_pending_comments()
        return [CommentInfo(**comment) for comment in comments]
    except Exception as e:
        logger.error(f"Error getting pending comments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events", response_model=List[EventInfo])
async def get_events(days_ahead: int = 30, db: Session = Depends(get_db)):
    """Get events from database"""
    try:
        events = db.query(EventDetails).all()
        result = []
        for event in events:
            # Format date and time in IST
            dt = datetime.combine(event.Date, event.Time)
            dt_ist = IST.localize(dt)
            result.append(EventInfo(
                event_id=event.EventID,
                title=event.Title,
                date=dt_ist.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
                time=dt_ist.strftime("%H:%M:%S %Z%z"),
                description=event.Description or "",
                registration_link=event.RegistrationLink,
                is_recorded=event.IsRecorded or "No"
            ))
        return result
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ai-responses", response_model=List[AIResponseInfo])
async def get_ai_responses(db: Session = Depends(get_db)):
    """Get all AI response templates"""
    try:
        responses = db.query(AIResponses).all()
        
        result = []
        for response in responses:
            result.append(AIResponseInfo(
                response_id=response.ResponseID,
                trigger_type=response.TriggerType,
                keyword_match=response.KeywordMatch,
                response_text=response.ResponseText
            ))
        
        return result
    except Exception as e:
        logger.error(f"Error getting AI responses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai-responses")
async def create_ai_response(
    trigger_type: str,
    response_text: str,
    keyword_match: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new AI response template"""
    try:
        import uuid
        response_id = f"RESP{str(uuid.uuid4())[:8].upper()}"
        
        new_response = AIResponses(
            ResponseID=response_id,
            TriggerType=trigger_type,
            KeywordMatch=keyword_match,
            ResponseText=response_text
        )
        
        db.add(new_response)
        db.commit()
        
        return {"success": True, "response_id": response_id}
    except Exception as e:
        logger.error(f"Error creating AI response: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/platforms")
async def get_platforms():
    """Get supported social media platforms"""
    return {
        "platforms": [
            # {
            #     "name": "LinkedIn",
            #     "id": "linkedin",
            #     "features": ["posts", "comments", "scheduling"]
            # },
            {
                "name": "Twitter/X",
                "id": "twitter",
                "features": ["posts", "comments", "scheduling"]
            },
            {
                "name": "Dev.to",
                "id": "devto",
                "features": ["articles", "comments", "scheduling", "markdown"]
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S %Z%z")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        # Get counts from database
        post_count = db.query(SocialMediaPosts).count()
        comment_count = db.query(SocialMediaComments).count()
        event_count = db.query(EventDetails).count()
        response_count = db.query(AIResponses).count()
        # Get pending comments count
        pending_comments = db.query(SocialMediaComments).filter(
            SocialMediaComments.ResponseStatus == "Pending"
        ).count()
        return {
            "total_posts": post_count,
            "total_comments": comment_count,
            "pending_comments": pending_comments,
            "total_events": event_count,
            "ai_responses": response_count,
            "last_updated": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S %Z%z")
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-comment-monitoring")
async def trigger_comment_monitoring(post_id: str, platform: str):
    """Manually trigger comment monitoring for a specific post"""
    try:
        result = scheduler.trigger_comment_monitoring(post_id, platform)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        logger.error(f"Error triggering comment monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comment-stats")
async def get_comment_stats():
    """Get detailed comment statistics"""
    try:
        result = scheduler.get_comment_stats()
        if result["success"]:
            return result["stats"]
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        logger.error(f"Error getting comment stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class EditPostRequest(BaseModel):
    new_content: Optional[str] = None
    new_time: Optional[str] = None  # ISO format datetime string

@app.put("/scheduled-posts/{post_id}")
async def edit_scheduled_post(post_id: str, request: EditPostRequest):
    """Edit a scheduled post's content and/or time"""
    try:
        new_time = None
        if request.new_time:
            try:
                new_time = datetime.fromisoformat(request.new_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        result = scheduler.edit_scheduled_post(post_id, request.new_content, new_time)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        logger.error(f"Error editing scheduled post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/scheduled-posts/{post_id}")
async def cancel_scheduled_post(post_id: str, platform: str):
    """Cancel a scheduled post"""
    try:
        result = scheduler.cancel_scheduled_post(post_id, platform)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        logger.error(f"Error cancelling scheduled post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/posts")
async def debug_posts(db: Session = Depends(get_db)):
    """Debug endpoint to check all posts and their statuses"""
    try:
        from app.models import SocialMediaPosts
        posts = db.query(SocialMediaPosts).all()
        
        result = []
        for post in posts:
            result.append({
                "post_id": post.PostID,
                "platform": post.Platform,
                "status": post.Status,
                "scheduled_time": f"{post.PostDate} {post.PostTime}" if post.PostDate and post.PostTime else None,
                "content_preview": post.ContentPreview[:100] + "..." if post.ContentPreview else None
            })
        
        return {
            "total_posts": len(result),
            "posts": result,
            "status_counts": {
                "Scheduled": len([p for p in result if p["status"] == "Scheduled"]),
                "Cancelled": len([p for p in result if p["status"] == "Cancelled"]),
                "Published": len([p for p in result if p["status"] == "Published"]),
                "Failed": len([p for p in result if p["status"] == "Failed"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 