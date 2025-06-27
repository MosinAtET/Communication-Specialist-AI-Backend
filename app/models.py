from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class PostStatus(enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class ResponseStatus(enum.Enum):
    PENDING = "pending"
    RESPONDED = "responded"
    ESCALATED = "escalated"

class CommentClassification(enum.Enum):
    EVENT_RELATED = "event-related"
    OFF_TOPIC = "off-topic"
    SPAM = "spam"
    NEGATIVE = "negative"
    ACCESSIBILITY = "accessibility"

class EventDetails(Base):
    __tablename__ = "EventDetails"
    
    EventID = Column(String(10), primary_key=True)
    Title = Column(String(255), nullable=False)
    Date = Column(Date, nullable=False)
    Time = Column(Time, nullable=False)
    Description = Column(Text, nullable=True)
    RegistrationLink = Column(String(500), nullable=True)
    IsRecorded = Column(String(10), nullable=True)  # 'Yes' or 'No'
    
    # Relationships
    posts = relationship("SocialMediaPosts", back_populates="event")

class SocialMediaPosts(Base):
    __tablename__ = "SocialMediaPosts"
    
    PostID = Column(String(10), primary_key=True)
    Platform = Column(String(100), nullable=False)  # linkedin, facebook, twitter, instagram
    PostDate = Column(Date, nullable=False)
    PostTime = Column(Time, nullable=False)
    ContentPreview = Column(String(4000), nullable=True)
    CampaignTag = Column(String(100), nullable=True)
    Status = Column(String(50), default="Scheduled")
    EventID = Column(String(10), ForeignKey("EventDetails.EventID"), nullable=True)
    PlatformPostID = Column(String(100), nullable=True)  # Real post/article/tweet ID from the platform
    
    # Relationships
    event = relationship("EventDetails", back_populates="posts")
    comments = relationship("SocialMediaComments", back_populates="post")

class SocialMediaComments(Base):
    __tablename__ = "SocialMediaComments"
    
    CommentID = Column(String(10), primary_key=True)
    PostID = Column(String(10), ForeignKey("SocialMediaPosts.PostID"), nullable=True)
    UserName = Column(String(100), nullable=True)
    CommentText = Column(Text, nullable=True)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    ResponseStatus = Column(String(50), default="Pending")
    Classification = Column(String(100), nullable=True)
    RetryCount = Column(Integer, default=0)
    
    # Relationships
    post = relationship("SocialMediaPosts", back_populates="comments")

class AIResponses(Base):
    __tablename__ = "AIResponses"
    
    ResponseID = Column(String(10), primary_key=True)
    TriggerType = Column(String(100), nullable=True)
    KeywordMatch = Column(String(100), nullable=True)
    ResponseText = Column(Text, nullable=True)

# Additional tables for enhanced functionality (optional)
class CommentResponses(Base):
    __tablename__ = "CommentResponses"
    
    ResponseID = Column(String(10), primary_key=True)
    CommentID = Column(String(10), ForeignKey("SocialMediaComments.CommentID"), nullable=False)
    AIResponseID = Column(String(10), ForeignKey("AIResponses.ResponseID"), nullable=False)
    ResponseText = Column(Text, nullable=False)
    PlatformResponseID = Column(String(100), nullable=True)  # ID from the platform
    SentAt = Column(DateTime, default=datetime.utcnow)
    Status = Column(String(50), default="sent")  # sent, failed, pending
    
    # Relationships
    comment = relationship("SocialMediaComments")
    ai_response = relationship("AIResponses")

class AuditLog(Base):
    __tablename__ = "AuditLog"
    
    LogID = Column(String(15), primary_key=True)
    Action = Column(String(100), nullable=False)  # post_scheduled, comment_responded, etc.
    EntityType = Column(String(50), nullable=False)  # post, comment, event
    EntityID = Column(String(10), nullable=True)
    Details = Column(Text, nullable=True)
    UserID = Column(String(100), nullable=True)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    Status = Column(String(50), default="success")  # success, failed, pending 