import google.generativeai as genai
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
import re
import logging
import os
from dotenv import load_dotenv
import pytz
load_dotenv()

logger = logging.getLogger(__name__)

class AICommunicationAgent:
    def __init__(self):
        """Initialize the AI Communication Agent with Gemini"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup prompt templates for different tasks"""
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day
        
        self.date_parsing_prompt = f"""
        Parse the date and time from the following user input. 
        Return only the parsed date and time in ISO format (YYYY-MM-DD HH:MM).
        If no specific time is mentioned, use 10:00 AM as default.
        
        CRITICAL: Today's date is {current_year}-{current_month:02d}-{current_day:02d}.
        When user says "today", "this morning", "this afternoon", etc., use today's actual date.
        When user says "tomorrow", use tomorrow's date.
        When user says "next [day]", calculate from today's date.
        When user says "immediately", "now", "right now", "asap", use current time + 2 minutes.
        
        IMPORTANT: Treat all times as local time (IST - India Standard Time). 
        Do NOT convert to UTC. Return the time exactly as specified by the user.
        
        User input: {{user_input}}
        
        Examples (assuming today is {current_year}-{current_month:02d}-{current_day:02d}):
        - "today at 8:18 AM" → {current_year}-{current_month:02d}-{current_day:02d} 08:18
        - "today at 2 PM" → {current_year}-{current_month:02d}-{current_day:02d} 14:00
        - "tomorrow at 3 PM" → {current_year}-{current_month:02d}-{(current_day + 1):02d} 15:00
        - "8:18 AM" → {current_year}-{current_month:02d}-{current_day:02d} 08:18
        - "this morning" → {current_year}-{current_month:02d}-{current_day:02d} 10:00
        - "immediately" → {current_year}-{current_month:02d}-{current_day:02d} {(current_date.hour + 1) % 24:02d}:{(current_date.minute + 2) % 60:02d}
        - "now" → {current_year}-{current_month:02d}-{current_day:02d} {(current_date.hour + 1) % 24:02d}:{(current_date.minute + 2) % 60:02d}
        
        Parsed date and time (local time):
        """
        
        self.content_generation_prompt = """
        Create a social media post for {platform} about the following event:
        
        Event: {event_title}
        Description: {event_description}
        Date: {event_date}
        Registration: {registration_link}
        
        Platform-specific requirements:
        - Tone: {tone}
        - Platform: {platform}
        
        Create engaging, platform-optimized content that encourages registration.
        Include relevant hashtags and call-to-action.
        
        Do not exceed 500 characters.
        
        For LinkedIn: Return only ONE concise, plain text post. Do NOT use markdown, bold, headings, numbering, or options. Do NOT return multiple options. Do NOT use asterisks or any formatting. Just return a simple text post.
        
        Post content:
        """
        
        self.comment_classification_prompt = """
        Classify the following comment based on its intent regarding the event:
        
        Event: {event_title}
        Event Description: {event_description}
        
        Comment: {comment_text}
        
        Classify as one of:
        - event-related: Questions about the event, registration, recording, etc.
        - off-topic: General conversation not related to the event
        - spam: Unwanted promotional content
        - negative: Critical feedback about the event or organization
        - accessibility: Questions about accessibility accommodations
        
        Also provide a confidence score (0-100) and brief reasoning.
        
        Classification:
        """
        
        self.response_generation_prompt = """
        Generate a helpful response to the following comment:
        
        Comment: {comment_text}
        Classification: {classification}
        Event: {event_title}
        Registration Link: {registration_link}
        Will be recorded: {is_recorded}
        
        Guidelines:
        - Be friendly and professional
        - Provide specific, helpful information
        - Keep responses concise but informative
        - For event-related questions, include relevant details
        - For off-topic comments, politely redirect to event questions
        
        Response:
        """
    
    def _call_ai(self, prompt: str) -> str:
        """Make a call to the AI model"""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error calling AI model: {e}")
            raise
    
    def parse_schedule_request(self, user_input: str) -> Dict[str, Any]:
        """Parse natural language scheduling requests"""
        try:
            # Check for immediate posting requests first
            user_input_lower = user_input.lower()
            immediate_keywords = ['immediately', 'now', 'right now', 'asap', 'as soon as possible']
            
            if any(keyword in user_input_lower for keyword in immediate_keywords):
                # Set time to current time + 2 minutes for immediate posting
                current_time = datetime.now()
                immediate_time = current_time + timedelta(minutes=2)
                
                logger.info(f"User requested immediate posting, setting time to: {immediate_time}")
                
                # Treat as IST and convert to UTC
                ist = pytz.timezone('Asia/Kolkata')
                immediate_time_ist = ist.localize(immediate_time.replace(tzinfo=None))
                immediate_time_utc = immediate_time_ist.astimezone(pytz.utc)
                
                return {
                    "success": True,
                    "datetime": immediate_time_utc,
                    "confidence": 0.95,
                    "immediate": True
                }
            
            prompt = self.date_parsing_prompt.format(user_input=user_input)
            result = self._call_ai(prompt)
            
            # Extract date and time from result
            date_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', result)
            if date_match:
                parsed_datetime = datetime.fromisoformat(date_match.group(1))
                
                # Get current date for validation
                current_date = datetime.now()
                
                # If user mentioned "today" or similar, ensure we're using today's date
                if any(word in user_input_lower for word in ['today', 'this morning', 'this afternoon', 'this evening', 'tonight']):
                    # Force today's date if user explicitly mentioned "today"
                    parsed_datetime = parsed_datetime.replace(
                        year=current_date.year,
                        month=current_date.month,
                        day=current_date.day
                    )
                    logger.info(f"User mentioned 'today', forcing date to: {parsed_datetime.date()}")
                
                # Ensure the parsed date is not in the past (unless it's today)
                if parsed_datetime.date() < current_date.date():
                    logger.warning(f"Parsed date {parsed_datetime.date()} is in the past, adjusting to today")
                    parsed_datetime = parsed_datetime.replace(
                        year=current_date.year,
                        month=current_date.month,
                        day=current_date.day
                    )
                
                # Treat the parsed datetime as IST (local time) and convert to UTC
                ist = pytz.timezone('Asia/Kolkata')
                if parsed_datetime.tzinfo is None:
                    # Assume the parsed time is in IST
                    parsed_datetime_ist = ist.localize(parsed_datetime)
                    # Convert to UTC for storage
                    parsed_datetime = parsed_datetime_ist.astimezone(pytz.utc)
                
                logger.info(f"Final parsed datetime: {parsed_datetime} (UTC)")
                
                return {
                    "success": True,
                    "datetime": parsed_datetime,
                    "confidence": 0.9
                }
            else:
                return {
                    "success": False,
                    "error": "Could not parse date and time",
                    "confidence": 0.0
                }
        except Exception as e:
            logger.error(f"Error parsing schedule request: {e}")
            return {
                "success": False,
                "error": str(e),
                "confidence": 0.0
            }
    
    def generate_platform_content(self, platform: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate platform-specific content for social media posts"""
        try:
            # Platform configurations
            platform_configs = {
                "linkedin": {"tone": "professional", "max_length": 300, "hashtag_limit": 5},
                "twitter": {"tone": "conversational", "max_length": 280, "hashtag_limit": 3},
                "devto": {"tone": "technical", "max_length": 500, "hashtag_limit": 4, "supports_markdown": True}
            }
            
            platform_config = platform_configs.get(platform.lower(), {"tone": "professional", "max_length": 1000, "hashtag_limit": 5})
            
            # Special handling for Dev.to (technical blog posts)
            if platform.lower() == "devto":
                prompt = f"""
                Create a technical blog post for Dev.to about the following event:
                
                Event: {event_data.get("title", "")}
                Description: {event_data.get("description", "")}
                Date: {event_data.get("date", "")}
                Registration: {event_data.get("registration_link", "")}
                
                Requirements:
                - Tone: Technical and informative
                - Format: Markdown with proper headings, code blocks if relevant
                - Include: Introduction, event details, why to attend, registration info
                - Hashtags: Up to 8 relevant technical hashtags
                - Length: 250-500 words
                
                Create an engaging technical blog post that encourages developers to register.
                Use markdown formatting with # for main title, ## for sections, and ### for subsections.
                Do not write the word markdown in the post. Just use the markdown formatting.
                
                Blog post content:
                """
            else:
                prompt = self.content_generation_prompt.format(
                    platform=platform,
                    event_title=event_data.get("title", ""),
                    event_description=event_data.get("description", ""),
                    event_date=event_data.get("date", ""),
                    registration_link=event_data.get("registration_link", ""),
                    tone=platform_config.get("tone", "professional")
                )
            
            result = self._call_ai(prompt)
            
            return {
                "success": True,
                "content": result.strip(),
                "platform": platform,
                "max_length": platform_config.get("max_length", 1000),
                "hashtag_limit": platform_config.get("hashtag_limit", 5),
                "supports_markdown": platform_config.get("supports_markdown", False)
            }
        except Exception as e:
            logger.error(f"Error generating content for {platform}: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }
    
    def classify_comment(self, comment_text: str, event_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Classify comment intent and determine appropriate response"""
        try:
            if not comment_text or not comment_text.strip():
                return {
                    "success": False,
                    "error": "Empty comment text",
                    "classification": "off-topic",
                    "should_respond": False
                }
            
            if event_data is None:
                event_data = {"title": "", "description": ""}
            
            prompt = self.comment_classification_prompt.format(
                comment_text=comment_text,
                event_title=event_data.get("title", ""),
                event_description=event_data.get("description", "")
            )
            
            result = self._call_ai(prompt)
            
            # Parse the classification result
            lines = result.strip().split('\n')
            classification = "event-related"  # default
            confidence = 50  # default
            reasoning = ""
            should_respond = True
            
            for line in lines:
                line_lower = line.lower()
                if any(cat in line_lower for cat in ["event-related", "off-topic", "spam", "negative", "accessibility"]):
                    for cat in ["event-related", "off-topic", "spam", "negative", "accessibility"]:
                        if cat in line_lower:
                            classification = cat
                            break
                elif "confidence" in line_lower:
                    conf_match = re.search(r'(\d+)', line)
                    if conf_match:
                        confidence = int(conf_match.group(1))
                elif "reasoning" in line_lower:
                    reasoning = line.split(':')[-1].strip()
            
            # Determine if we should respond based on classification
            should_respond = classification in ["event-related", "accessibility"]
            
            # Additional validation for spam detection
            spam_indicators = ["buy now", "click here", "make money", "earn cash", "free money", "lottery", "winner", "urgent", "limited time"]
            if any(indicator in comment_text.lower() for indicator in spam_indicators):
                classification = "spam"
                confidence = 90
                should_respond = False
            
            # Additional validation for negative sentiment
            negative_indicators = ["terrible", "awful", "horrible", "worst", "hate", "disappointed", "angry", "frustrated"]
            if any(indicator in comment_text.lower() for indicator in negative_indicators):
                if classification == "event-related":
                    classification = "negative"
                    confidence = 80
            
            return {
                "success": True,
                "classification": classification,
                "confidence": confidence,
                "reasoning": reasoning,
                "should_respond": should_respond
            }
        except Exception as e:
            logger.error(f"Error classifying comment: {e}")
            return {
                "success": False,
                "error": str(e),
                "classification": "event-related",
                "should_respond": True
            }
    
    def generate_comment_response(self, comment_text: str, classification: str, event_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate appropriate response to a comment"""
        try:
            if event_data is None:
                event_data = {"title": "", "registration_link": "", "is_recorded": False}
            
            prompt = self.response_generation_prompt.format(
                comment_text=comment_text,
                classification=classification,
                event_title=event_data.get("title", ""),
                registration_link=event_data.get("registration_link", ""),
                is_recorded=event_data.get("is_recorded", False)
            )
            
            result = self._call_ai(prompt)
            
            return {
                "success": True,
                "response": result.strip(),
                "classification": classification
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Thank you for your comment! We'll get back to you soon."
            }
    
    def extract_event_keywords(self, text: str) -> List[str]:
        """Extract event-related keywords from text"""
        try:
            prompt = f"""
            Extract event-related keywords from the following text. 
            Focus on words related to events, webinars, meetings, conferences, etc.
            
            Text: {text}
            
            Return only the keywords separated by commas:
            """
            
            result = self._call_ai(prompt)
            keywords = [kw.strip().lower() for kw in result.split(',') if kw.strip()]
            return keywords[:10]  # Limit to 10 keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def find_matching_event(self, user_prompt: str, available_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Intelligently find the most relevant event based on user query"""
        try:
            if not available_events:
                return {"success": False, "error": "No events available"}
            
            # Create a detailed prompt for event matching
            events_info = []
            for i, event in enumerate(available_events):
                event_date = event.get('Date', '')
                event_time = event.get('Time', '')
                if isinstance(event_date, str):
                    formatted_date = event_date
                else:
                    formatted_date = event_date.strftime("%B %d, %Y") if event_date else "No date"
                
                if isinstance(event_time, str):
                    formatted_time = event_time
                else:
                    formatted_time = event_time.strftime("%I:%M %p") if event_time else "No time"
                
                events_info.append(f"""
Event {i+1}:
- Title: {event.get('Title', 'N/A')}
- Date: {formatted_date}
- Time: {formatted_time}
- Description: {event.get('Description', 'N/A')}
- ID: {event.get('EventID', 'N/A')}
""")
            
            prompt = f"""
            Based on the user's query, determine which event they are referring to.
            
            User Query: "{user_prompt}"
            
            Available Events:
            {''.join(events_info)}
            
            Instructions:
            1. Analyze the user's query for:
               - Event names, titles, or topics mentioned
               - Dates mentioned (today, tomorrow, specific dates)
               - Time references
               - Event types (webinar, conference, meeting, etc.)
               - Any specific details that match event descriptions
            
            2. Consider:
               - Exact title matches
               - Partial title matches
               - Date relevance (if user mentions "today's webinar", match today's events)
               - Topic similarity
               - Event type matching
            
            3. Return the Event ID of the best match, or "none" if no good match found.
            
            4. If multiple events could match, choose the most recent one that fits the context.
            
            Return only the Event ID (e.g., "EVT001") or "none":
            """
            
            result = self._call_ai(prompt).strip()
            
            # Extract event ID from result
            event_id_match = re.search(r'EVT\d+', result, re.IGNORECASE)
            if event_id_match:
                event_id = event_id_match.group(0).upper()
                # Find the matching event
                for event in available_events:
                    if event.get('EventID', '').upper() == event_id:
                        logger.info(f"AI matched event: {event.get('Title', 'Unknown')} (ID: {event_id})")
                        return {
                            "success": True,
                            "event": event,
                            "confidence": 0.9,
                            "reasoning": f"Matched based on user query context"
                        }
            
            # If no specific match found, try fuzzy matching
            logger.info("No specific event ID found, trying fuzzy matching...")
            return self._fuzzy_event_match(user_prompt, available_events)
            
        except Exception as e:
            logger.error(f"Error in find_matching_event: {e}")
            return {"success": False, "error": str(e)}
    
    def _fuzzy_event_match(self, user_prompt: str, available_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback fuzzy matching when AI doesn't return a specific event ID"""
        try:
            user_lower = user_prompt.lower()
            
            # Score each event based on various criteria
            scored_events = []
            
            for event in available_events:
                score = 0
                title = event.get('Title', '').lower()
                description = event.get('Description', '').lower()
                
                # Title exact match (highest score)
                if title in user_lower or user_lower in title:
                    score += 100
                
                # Title word matches
                title_words = title.split()
                for word in title_words:
                    if len(word) > 3 and word in user_lower:  # Only significant words
                        score += 20
                
                # Description matches
                if description and any(word in description for word in user_lower.split() if len(word) > 3):
                    score += 10
                
                # Date relevance (if user mentions today/tomorrow)
                event_date = event.get('Date')
                if event_date:
                    current_date = datetime.now().date()
                    parsed_event_date = None
                    
                    # Handle different date formats
                    if isinstance(event_date, str):
                        try:
                            parsed_event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
                        except ValueError:
                            try:
                                parsed_event_date = datetime.strptime(event_date, "%Y-%m-%d %H:%M:%S").date()
                            except ValueError:
                                parsed_event_date = None
                    elif isinstance(event_date, date):
                        parsed_event_date = event_date
                    elif isinstance(event_date, datetime):
                        parsed_event_date = event_date.date()
                    
                    if parsed_event_date:
                        if "today" in user_lower and parsed_event_date == current_date:
                            score += 50
                        elif "tomorrow" in user_lower and parsed_event_date == current_date + timedelta(days=1):
                            score += 50
                        elif "this week" in user_lower and (parsed_event_date - current_date).days <= 7:
                            score += 30
                        
                        # Recency bonus (prefer recent events)
                        days_diff = (current_date - parsed_event_date).days
                        if days_diff <= 30:  # Within last month
                            score += 5
                
                scored_events.append((event, score))
            
            # Sort by score and return the best match
            scored_events.sort(key=lambda x: x[1], reverse=True)
            
            if scored_events and scored_events[0][1] > 0:
                best_event, best_score = scored_events[0]
                logger.info(f"Fuzzy matched event: {best_event.get('Title', 'Unknown')} (score: {best_score})")
                return {
                    "success": True,
                    "event": best_event,
                    "confidence": min(0.8, best_score / 100),  # Normalize confidence
                    "reasoning": f"Fuzzy matched with score {best_score}"
                }
            else:
                # Return the most recent event as last resort
                def get_event_date(event):
                    event_date = event.get('Date')
                    if isinstance(event_date, str):
                        try:
                            return datetime.strptime(event_date, "%Y-%m-%d").date()
                        except ValueError:
                            try:
                                return datetime.strptime(event_date, "%Y-%m-%d %H:%M:%S").date()
                            except ValueError:
                                return datetime.min.date()
                    elif isinstance(event_date, date):
                        return event_date
                    elif isinstance(event_date, datetime):
                        return event_date.date()
                    else:
                        return datetime.min.date()
                
                most_recent = max(available_events, key=get_event_date)
                logger.info(f"No good match found, using most recent event: {most_recent.get('Title', 'Unknown')}")
                return {
                    "success": True,
                    "event": most_recent,
                    "confidence": 0.3,
                    "reasoning": "Using most recent event as fallback"
                }
                
        except Exception as e:
            logger.error(f"Error in fuzzy event matching: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_response(self, comment_text: str, classification: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method for backward compatibility"""
        return self.generate_comment_response(comment_text, classification, event_data) 