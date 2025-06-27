from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from app.database import SessionLocal
from app.models import SocialMediaPosts, SocialMediaComments, EventDetails, AuditLog, AIResponses
from app.ai_agent import AICommunicationAgent
from app.social_media_platforms import SocialMediaManager
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date, time
import logging
import uuid
import os
from dotenv import load_dotenv
import pytz
from bs4 import BeautifulSoup

load_dotenv()

logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Kolkata')

# --- TOP-LEVEL FUNCTION FOR APSCHEDULER JOBS ---
def publish_scheduled_post(post_id: str, platform: str):
    """Top-level function for APScheduler to call for publishing posts."""
    from app.scheduler import CommunicationScheduler
    scheduler = CommunicationScheduler()
    scheduler._publish_scheduled_post(post_id, platform)

class CommunicationScheduler:
    """Main scheduler for managing social media posts and comment monitoring"""
    
    def __init__(self):
        """Initialize the scheduler with job stores and executors"""
        # Use SQL Server connection string for job store
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "mssql+pyodbc://sa:YourPassword@localhost/SocialMediaAI?driver=ODBC+Driver+17+for+SQL+Server"
        )
        
        self.scheduler = BackgroundScheduler(
            jobstores={
                'default': SQLAlchemyJobStore(url=DATABASE_URL)
            },
            executors={
                'default': ThreadPoolExecutor(5)  # Reduced from 20 to 5 to prevent connection conflicts
            },
            job_defaults={
                'coalesce': True,  # Combine multiple pending jobs of the same type
                'max_instances': 1,  # Only allow 1 instance of each job
                'misfire_grace_time': 60  # Grace period for misfired jobs
            }
        )
        
        self.ai_agent = AICommunicationAgent()
        self.social_media_manager = SocialMediaManager()
        
        # Start the scheduler
        self.scheduler.start()
        logger.info("Communication scheduler started")
    
    def schedule_post(self, user_prompt: str, platforms: List[str] = None) -> Dict[str, Any]:
        """Schedule posts based on user prompt"""
        try:
            # Parse the scheduling request
            schedule_result = self.ai_agent.parse_schedule_request(user_prompt)
            if not schedule_result["success"]:
                return {"success": False, "error": schedule_result["error"]}
            
            # Convert scheduled_time to IST and make it timezone-aware
            scheduled_time = schedule_result["datetime"]
            is_immediate = schedule_result.get("immediate", False)
            logger.info(f"AI parsed datetime (UTC): {scheduled_time}")
            
            if scheduled_time.tzinfo is None:
                scheduled_time = pytz.utc.localize(scheduled_time)
            scheduled_time_ist = scheduled_time.astimezone(IST)
            logger.info(f"Converted to IST: {scheduled_time_ist}")
            
            if is_immediate:
                logger.info("Scheduling immediate post (within 2 minutes)")
            
            # Get all available events from database
            db = SessionLocal()
            try:
                all_events = db.query(EventDetails).order_by(EventDetails.Date.desc()).all()
                if not all_events:
                    db.close()
                    return {
                        "success": False, 
                        "error": "No events found in the database. Please add some events first.",
                        "scheduled_posts": {},
                        "event": {
                            "title": "Error",
                            "date": "",
                            "description": ""
                        }
                    }
                
                # Convert events to dictionary format for AI processing
                available_events = []
                for event in all_events:
                    available_events.append({
                        'EventID': event.EventID,
                        'Title': event.Title,
                        'Description': event.Description or "",
                        'Date': event.Date,
                        'Time': event.Time,
                        'RegistrationLink': event.RegistrationLink or ""
                    })
                
                # Use AI to find the most relevant event based on user query
                event_match_result = self.ai_agent.find_matching_event(user_prompt, available_events)
                
                if not event_match_result["success"]:
                    db.close()
                    return {
                        "success": False, 
                        "error": f"Failed to match event: {event_match_result.get('error', 'Unknown error')}",
                        "scheduled_posts": {},
                        "event": {
                            "title": "Error",
                            "date": "",
                            "description": ""
                        }
                    }
                
                matched_event = event_match_result["event"]
                confidence = event_match_result.get("confidence", 0.5)
                reasoning = event_match_result.get("reasoning", "Unknown")
                
                logger.info(f"Event matched: {matched_event['Title']} (confidence: {confidence:.2f}, reasoning: {reasoning})")
                
                # If confidence is low, warn the user but proceed
                if confidence < 0.5:
                    logger.warning(f"Low confidence event match ({confidence:.2f}): {matched_event['Title']}")
                
                event_data = {
                    "id": matched_event["EventID"],
                    "title": matched_event["Title"],
                    "description": matched_event["Description"],
                    "start_date": datetime.combine(matched_event["Date"], matched_event["Time"]).replace(tzinfo=IST),
                    "time": matched_event["Time"].strftime("%H:%M:%S"),
                    "html_link": matched_event["RegistrationLink"]
                }
                
            except Exception as e:
                db.close()
                logger.error(f"Database error in event matching: {e}")
                return {
                    "success": False, 
                    "error": f"Database error: {str(e)}",
                    "scheduled_posts": {},
                    "event": {
                        "title": "Error",
                        "date": "",
                        "description": ""
                    }
                }
            finally:
                db.close()
            
            # Generate platform-specific content
            if platforms is None:
                platforms = ["devto"]  # Only Dev.to for now
            
            # Filter out platforms that are not available
            available_platforms = self.social_media_manager.get_available_platforms()
            platforms = [p for p in platforms if p in available_platforms]
            
            if not platforms:
                return {
                    "success": False, 
                    "error": "No available platforms found. Please check your platform configuration.",
                    "scheduled_posts": {},
                    "event": {
                        "title": "Error",
                        "date": "",
                        "description": ""
                    }
                }
            
            scheduled_posts = {}
            
            for platform in platforms:
                # Generate content for this platform
                content_result = self.ai_agent.generate_platform_content(platform, {
                    "title": event_data["title"],
                    "description": event_data["description"],
                    "date": event_data["start_date"].strftime("%B %d, %Y at %I:%M %p"),
                    "registration_link": event_data.get("html_link", "")
                })
                
                if not content_result["success"]:
                    logger.error(f"Failed to generate content for {platform}: {content_result['error']}")
                    continue
                
                # Save the post to the database with status 'Scheduled'
                post_id = f"P{str(uuid.uuid4())[:8].upper()}"
                db = SessionLocal()
                try:
                    # Save event if not exists
                    event_db = db.query(EventDetails).filter_by(EventID=event_data["id"]).first()
                    if not event_db:
                        event_db = EventDetails(
                            EventID=event_data["id"],
                            Title=event_data["title"],
                            Date=event_data["start_date"].date(),
                            Time=event_data["start_date"].time(),
                            Description=event_data["description"],
                            RegistrationLink=event_data.get("html_link", ""),
                            IsRecorded="No"
                        )
                        db.add(event_db)
                        db.commit()
                    # Ensure scheduled_time_ist is timezone-aware and in IST
                    if scheduled_time_ist.tzinfo is None or scheduled_time_ist.tzinfo.zone != IST.zone:
                        scheduled_time_ist = IST.localize(scheduled_time_ist.replace(tzinfo=None))
                    # Save post
                    logger.info(f"Saving post with IST date: {scheduled_time_ist.date()}, time: {scheduled_time_ist.time()} (tz: {scheduled_time_ist.tzinfo})")
                    post_db = SocialMediaPosts(
                        PostID=post_id,
                        Platform=platform,
                        PostDate=scheduled_time_ist.date(),
                        PostTime=scheduled_time_ist.time(),
                        ContentPreview=content_result["content"],
                        CampaignTag=f"#{event_data['title'].replace(' ', '')}",
                        Status="Scheduled",
                        EventID=event_data["id"],
                        PlatformPostID=None  # Not known until published
                    )
                    db.add(post_db)
                    # Log the action
                    audit_log = AuditLog(
                        LogID=f"LOG{str(uuid.uuid4())[:8].upper()}",
                        Action="post_scheduled",
                        EntityType="post",
                        EntityID=post_id,
                        Details=f"Scheduled {platform} post for {event_data['title']}",
                        Status="success"
                    )
                    db.add(audit_log)
                    db.commit()
                    scheduled_posts[platform] = {
                        "post_id": post_id,
                        "content": content_result["content"],
                        "scheduled_time": scheduled_time_ist.strftime("%Y-%m-%d %H:%M:%S %Z%z")
                    }
                    # Schedule the actual posting job
                    job_id = f"publish_{post_id}_{platform}"
                    from app.scheduler import publish_scheduled_post
                    self.scheduler.add_job(
                        func=publish_scheduled_post,
                        trigger=DateTrigger(run_date=scheduled_time_ist),
                        args=[post_id, platform],
                        id=job_id,
                        replace_existing=True
                    )
                except Exception as e:
                    import traceback
                    logger.error(f"Database error saving post: {e}\n{traceback.format_exc()}")
                    db.rollback()
                finally:
                    db.close()
            return {
                "success": True,
                "scheduled_posts": scheduled_posts,
                "event": {
                    "title": event_data["title"],
                    "date": event_data["start_date"].astimezone(IST).strftime("%Y-%m-%d %H:%M:%S %Z%z"),
                    "description": event_data["description"]
                },
                "immediate": is_immediate,
                "message": "Post scheduled for immediate publishing (within 2 minutes)" if is_immediate else "Post scheduled successfully",
                "event_matching": {
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "matched_event_title": event_data["title"]
                }
            }
        except Exception as e:
            logger.error(f"Error scheduling post: {e}")
            return {
                "success": False, 
                "error": str(e),
                "scheduled_posts": {},
                "event": {
                    "title": "Error",
                    "date": "",
                    "description": ""
                }
            }

    def edit_scheduled_post(self, post_id: str, new_content: Optional[str] = None, new_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Edit the content and/or scheduled time of a scheduled post"""
        db = SessionLocal()
        try:
            post = db.query(SocialMediaPosts).filter_by(PostID=post_id, Status="Scheduled").first()
            if not post:
                return {"success": False, "error": "Scheduled post not found or already published."}
            if new_content:
                post.ContentPreview = new_content
            if new_time:
                # Convert new_time to IST
                if new_time.tzinfo is None:
                    new_time = pytz.utc.localize(new_time)
                new_time_ist = new_time.astimezone(IST)
                post.PostDate = new_time_ist.date()
                post.PostTime = new_time_ist.time()
                # Reschedule the APScheduler job
                job_id = f"publish_{post_id}_{post.Platform}"
                self.scheduler.reschedule_job(job_id, trigger=DateTrigger(run_date=new_time_ist))
            db.commit()
            return {"success": True, "message": "Scheduled post updated."}
        except Exception as e:
            db.rollback()
            logger.error(f"Error editing scheduled post: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def cancel_scheduled_post(self, post_id: str, platform: str) -> Dict[str, Any]:
        """Cancel a scheduled post and remove its job"""
        db = SessionLocal()
        try:
            post = db.query(SocialMediaPosts).filter_by(PostID=post_id, Platform=platform, Status="Scheduled").first()
            if not post:
                return {"success": False, "error": "Scheduled post not found or already published."}
            post.Status = "Cancelled"
            db.commit()
            # Remove the scheduled job
            job_id = f"publish_{post_id}_{platform}"
            try:
                self.scheduler.remove_job(job_id)
            except Exception as e:
                logger.warning(f"Job removal warning: {e}")
            return {"success": True, "message": "Scheduled post cancelled."}
        except Exception as e:
            db.rollback()
            logger.error(f"Error cancelling scheduled post: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def _publish_scheduled_post(self, post_id: str, platform: str):
        """Publish the scheduled post to the real platform and update status, with notification"""
        db = None
        try:
            db = SessionLocal()
            post = db.query(SocialMediaPosts).filter_by(PostID=post_id, Platform=platform).first()
            if not post:
                logger.error(f"Scheduled post {post_id} for {platform} not found in DB.")
                return
            if post.Status == "Published":
                logger.info(f"Post {post_id} for {platform} already published.")
                return
            if post.Status == "Cancelled":
                logger.info(f"Post {post_id} for {platform} was cancelled.")
                return
            # Get the content
            content = post.ContentPreview
            # Get the platform instance
            platform_instance = self.social_media_manager.get_platform(platform)
            if not platform_instance:
                logger.error(f"Platform {platform} not found for publishing post {post_id}.")
                self._send_notification(f"Failed to publish post {post_id} to {platform}: platform not found.")
                return
            # Actually post to the platform
            now_ist = datetime.now(IST)
            result = platform_instance.schedule_post(content, now_ist)
            if result.get("success"):
                post.Status = "Published"
                # Save the real platform post ID
                post.PlatformPostID = result.get("post_id", None)
                db.commit()
                logger.info(f"Published post {post_id} to {platform} at scheduled time.")
                self._send_notification(f"✅ Published post {post_id} to {platform} at scheduled time.")
                # Schedule comment monitoring after publishing
                self._schedule_comment_monitoring(post_id, platform, result.get("post_id", ""))
            else:
                post.Status = "Failed"
                db.commit()
                logger.error(f"Failed to publish post {post_id} to {platform}: {result.get('error')}")
                self._send_notification(f"❌ Failed to publish post {post_id} to {platform}: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error in _publish_scheduled_post: {e}")
            if db:
                db.rollback()
            self._send_notification(f"❌ Error in publishing post {post_id} to {platform}: {e}")
        finally:
            if db:
                db.close()

    def _send_notification(self, message: str):
        """Send a notification (currently logs, can be extended to email, Slack, etc.)"""
        logger.info(f"NOTIFICATION: {message}")

    def _schedule_comment_monitoring(self, post_id: str, platform: str, platform_post_id: str):
        """Schedule comment monitoring for a specific post"""
        try:
            db = None
            # Always fetch the latest platform_post_id from the DB if not provided
            if not platform_post_id:
                db = SessionLocal()
                post = db.query(SocialMediaPosts).filter_by(PostID=post_id, Platform=platform).first()
                platform_post_id = post.PlatformPostID if post else None
                if db:
                    db.close()
            logger.info(f"[DEBUG] Running _monitor_comments for post_id={post_id}, platform={platform}, platform_post_id={platform_post_id}")
            # Schedule monitoring to start 15 minutes after post time
            # and run every 15 minutes for 24 hours
            job_id = f"monitor_{post_id}_{platform}"
            
            # Remove existing job if any
            try:
                self.scheduler.remove_job(job_id)
            except Exception as e:
                logger.info(f"[DEBUG] No existing job to remove for {job_id}: {e}")
            
            # Schedule the monitoring job
            # Run every 15 minutes for better responsiveness
            self.scheduler.add_job(
                func=self._monitor_comments,
                trigger=CronTrigger(minute="*/15"),  # Every 15 minutes
                args=[post_id, platform, platform_post_id],
                id=job_id,
                max_instances=1,
                replace_existing=True
            )
            logger.info(f"[DEBUG] Scheduled comment monitoring job_id={job_id} for {platform} post {post_id}")
        except Exception as e:
            logger.error(f"[DEBUG] Error scheduling comment monitoring: {e}")
    
    @staticmethod
    def html_to_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def _monitor_comments(self, post_id: str, platform: str, platform_post_id: str):
        """Monitor comments for a specific post"""
        try:
            db = None
            # Always fetch the latest platform_post_id from the DB if not provided
            if not platform_post_id:
                db = SessionLocal()
                post = db.query(SocialMediaPosts).filter_by(PostID=post_id, Platform=platform).first()
                platform_post_id = post.PlatformPostID if post else None
                if db:
                    db.close()
            
            # Get platform instance
            platform_instance = self.social_media_manager.get_platform(platform)
            if not platform_instance:
                logger.error(f"❌ Platform {platform} not found for comment monitoring")
                return
            
            # Get comments from platform
            comments_result = platform_instance.get_comments(platform_post_id)
            if not comments_result["success"]:
                logger.error(f"❌ Failed to get comments from {platform}: {comments_result['error']}")
                return
            
            comments = comments_result["comments"]
            if len(comments) == 0:
                return  # No comments to process
            
            logger.info(f"📝 Processing {len(comments)} comments for {platform} post {post_id}")
            
            # Process each comment
            db = None
            try:
                db = SessionLocal()
                for comment in comments:
                    # Strict validation for comment_id
                    if not comment.get("comment_id") or not str(comment["comment_id"]).strip():
                        continue
                    
                    comment_id = str(comment["comment_id"]).strip()
                    
                    # Clean up comment text
                    cleaned_text = self.html_to_text(comment.get("text", ""))
                    if not cleaned_text.strip():
                        continue
                    
                    # Check if comment already exists
                    existing_comment = db.query(SocialMediaComments).filter_by(
                        CommentID=comment_id
                    ).first()
                    
                    retry_count = 0
                    if existing_comment:
                        if existing_comment.ResponseStatus == "Responded":
                            continue  # Already responded
                        retry_count = getattr(existing_comment, 'RetryCount', 0)
                        if retry_count >= 3:
                            existing_comment.ResponseStatus = "Escalated"
                            db.commit()
                            logger.warning(f"⚠️ Comment {comment_id} escalated after 3 retries")
                            continue
                        existing_comment.ResponseStatus = "Pending"
                        existing_comment.RetryCount = retry_count + 1
                        db.commit()
                    
                    # Classify the comment
                    try:
                        classification_result = self.ai_agent.classify_comment(cleaned_text)
                        classification = classification_result.get("classification", "event-related")
                    except Exception as e:
                        classification = "event-related"  # Default fallback
                    
                    # Generate AI response
                    try:
                        # Get event data for the post
                        post_with_event = db.query(SocialMediaPosts).filter_by(PostID=post_id).first()
                        event_data = {}
                        if post_with_event and post_with_event.event:
                            event_data = {
                                "title": post_with_event.event.Title or "",
                                "registration_link": post_with_event.event.RegistrationLink or "",
                                "is_recorded": post_with_event.event.IsRecorded or False
                            }
                        
                        response_result = self.ai_agent.generate_comment_response(cleaned_text, classification, event_data)
                        if not response_result.get("success"):
                            logger.error(f"❌ Failed to generate response for comment {comment_id}: {response_result.get('error')}")
                            response_status = "Failed"
                            send_result = {"success": False, "error": response_result.get("error")}
                        else:
                            response_text = response_result.get("response", "")
                            # Send the response
                            send_result = platform_instance.respond_to_comment(
                                comment_id, 
                                response_text,
                                parent_type="article",
                                parent_id=platform_post_id
                            )
                            response_status = "Responded" if send_result.get("success") else "Failed"
                    except Exception as e:
                        logger.error(f"❌ Exception while sending response to comment {comment_id}: {e}")
                        response_status = "Failed"
                        send_result = {"success": False, "error": str(e)}
                    
                    # Save or update comment in database
                    try:
                        if existing_comment:
                            existing_comment.ResponseStatus = response_status
                            existing_comment.CommentText = cleaned_text
                            existing_comment.Timestamp = comment.get("timestamp", datetime.now())
                            existing_comment.Classification = classification
                            existing_comment.RetryCount = retry_count + 1
                            db.commit()
                        else:
                            new_comment = SocialMediaComments(
                                CommentID=comment_id,
                                PostID=post_id,
                                UserName=comment.get("user_name", "Unknown"),
                                CommentText=cleaned_text,
                                Timestamp=comment.get("timestamp", datetime.now()),
                                ResponseStatus=response_status,
                                Classification=classification,
                                RetryCount=1
                            )
                            db.add(new_comment)
                            db.commit()
                        
                        # Log the response
                        audit_log = AuditLog(
                            LogID=f"LOG{str(uuid.uuid4())[:8].upper()}",
                            Action="comment_responded",
                            EntityType="comment",
                            EntityID=comment_id,
                            Details=f"Responded to comment on post {post_id} with classification {classification}",
                            Status="success" if send_result.get("success") else "failed"
                        )
                        db.add(audit_log)
                        db.commit()
                        
                        # Show result
                        if send_result.get("success"):
                            logger.info(f"✅ Successfully replied to comment {comment_id}")
                        else:
                            logger.error(f"❌ Failed to reply to comment {comment_id}: {send_result.get('error', 'Unknown error')}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to save comment {comment_id} to database: {e}")
                        db.rollback()
            except Exception as e:
                logger.error(f"❌ Error monitoring comments: {e}")
                if db:
                    db.rollback()
            finally:
                if db:
                    db.close()
        except Exception as e:
            logger.error(f"❌ Error in comment monitoring: {e}")
    
    def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Get all scheduled posts"""
        try:
            db = SessionLocal()
            posts = db.query(SocialMediaPosts).filter_by(Status="Scheduled").all()
            
            result = []
            for post in posts:
                result.append({
                    "post_id": post.PostID,
                    "platform": post.Platform,
                    "scheduled_time": f"{post.PostDate} {post.PostTime}",
                    "content_preview": post.ContentPreview,
                    "campaign_tag": post.CampaignTag,
                    "event_title": post.event.Title if post.event else None,
                    "platform_post_id": post.PlatformPostID
                })
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting scheduled posts: {e}")
            return []
    
    def get_pending_comments(self) -> List[Dict[str, Any]]:
        """Get all pending comments that need human review"""
        try:
            db = SessionLocal()
            comments = db.query(SocialMediaComments).filter_by(ResponseStatus="Pending").all()
            
            result = []
            for comment in comments:
                result.append({
                    "comment_id": comment.CommentID,
                    "post_id": comment.PostID,
                    "platform": comment.post.Platform if comment.post else "Unknown",
                    "user_name": comment.UserName,
                    "comment_text": comment.CommentText,
                    "classification": comment.Classification,
                    "timestamp": comment.Timestamp.isoformat()
                })
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting pending comments: {e}")
            return []
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Communication scheduler shutdown")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")

    def cleanup_disabled_platform_jobs(self):
        """Clean up scheduled jobs for disabled platforms"""
        try:
            disabled_platforms = ["linkedin"]
            removed_jobs = 0
            
            for platform in disabled_platforms:
                # Get all jobs for this platform
                jobs = self.scheduler.get_jobs()
                for job in jobs:
                    if job.args and len(job.args) >= 2 and job.args[1] == platform:
                        try:
                            self.scheduler.remove_job(job.id)
                            removed_jobs += 1
                            logger.info(f"Removed scheduled job {job.id} for {platform}")
                        except Exception as e:
                            logger.warning(f"Could not remove job {job.id}: {e}")
            
            logger.info(f"Cleaned up {removed_jobs} jobs for disabled platforms")
            return removed_jobs
            
        except Exception as e:
            logger.error(f"Error cleaning up disabled platform jobs: {e}")
            return 0

    def trigger_comment_monitoring(self, post_id: str, platform: str) -> Dict[str, Any]:
        """Manually trigger comment monitoring for a specific post (for testing/debugging)"""
        try:
            logger.info(f"Manually triggering comment monitoring for post {post_id} on {platform}")
            
            # Get the platform post ID from database
            db = SessionLocal()
            post = db.query(SocialMediaPosts).filter_by(PostID=post_id, Platform=platform).first()
            if not post:
                db.close()
                return {"success": False, "error": "Post not found"}
            
            platform_post_id = post.PlatformPostID
            db.close()
            
            if not platform_post_id:
                return {"success": False, "error": "Platform post ID not found"}
            
            # Trigger the monitoring
            self._monitor_comments(post_id, platform, platform_post_id)
            
            return {
                "success": True,
                "message": f"Comment monitoring triggered for post {post_id} on {platform}",
                "platform_post_id": platform_post_id
            }
            
        except Exception as e:
            logger.error(f"Error triggering comment monitoring: {e}")
            return {"success": False, "error": str(e)}
    
    def get_comment_stats(self) -> Dict[str, Any]:
        """Get statistics about comments and responses"""
        try:
            db = SessionLocal()
            
            total_comments = db.query(SocialMediaComments).count()
            pending_comments = db.query(SocialMediaComments).filter_by(ResponseStatus="Pending").count()
            responded_comments = db.query(SocialMediaComments).filter_by(ResponseStatus="Responded").count()
            failed_comments = db.query(SocialMediaComments).filter_by(ResponseStatus="Failed").count()
            escalated_comments = db.query(SocialMediaComments).filter_by(ResponseStatus="Escalated").count()
            
            # Get classification breakdown
            classifications = db.query(SocialMediaComments.Classification, db.func.count(SocialMediaComments.CommentID)).group_by(SocialMediaComments.Classification).all()
            
            db.close()
            
            return {
                "success": True,
                "stats": {
                    "total_comments": total_comments,
                    "pending_comments": pending_comments,
                    "responded_comments": responded_comments,
                    "failed_comments": failed_comments,
                    "escalated_comments": escalated_comments,
                    "classifications": dict(classifications)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting comment stats: {e}")
            return {"success": False, "error": str(e)} 