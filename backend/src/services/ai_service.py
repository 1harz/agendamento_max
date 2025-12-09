import google.generativeai as genai
import json
import logging
from typing import List, Dict, Any, Optional
from ..config import Config
from .appointment_service import AppointmentService
from ..models.appointment import Appointment, VolatilityLevel

logger = logging.getLogger("maxfrio-ai")

class AIService:
    def __init__(self):
        self.appointment_service = AppointmentService()
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        else:
            self.model = None
            logger.warning("Gemini API Key not found. AI features will be disabled.")

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.model:
            return {
                "message": "AI Service unavailable. Please check configuration.",
                "requires_confirmation": False
            }

        try:
            # Fetch current appointments to provide context
            appointments = await self.appointment_service.get_all_appointments()
            appointments_context = json.dumps([app.dict() for app in appointments], default=str)

            prompt = f"""
            You are a helpful assistant for Maxfrio, an HVAC service company.
            
            Current Date/Time: {context.get('current_time', 'Unknown')}
            
            Current Appointments:
            {appointments_context}
            
            User Message: {message}
            
            Task:
            Analyze the user's request and the current schedule.
            If the user wants to reschedule or cancel, identify the appointment and suggest actions.
            If the user asks for recommendations, analyze gaps and priorities.
            
            Response Format (JSON only):
            {{
                "message": "Natural language response to user",
                "action": {{
                    "type": "reschedule|recommend|cancel|info|none",
                    "appointment_id": "uuid or null",
                    "new_date": "ISO string or null",
                    "recommendation": "Appointment object or null"
                }},
                "requires_confirmation": boolean
            }}
            """

            response = self.model.generate_content(prompt)
            # Basic cleanup if model returns markdown code blocks
            text_response = response.text.replace('```json', '').replace('```', '').strip()
            
            try:
                return json.loads(text_response)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response: {text_response}")
                return {
                    "message": "Sorry, I couldn't process that request properly.",
                    "requires_confirmation": False
                }

        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            return {
                "message": "An error occurred while processing your request.",
                "requires_confirmation": False
            }

    async def get_recommendations(self, excluded_appointment_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Implements T046: Priority-based recommendation algorithm
        Logic:
        1. Filter pending appointments
        2. Score based on Volatility (High=1.0, Medium=0.6, Low=0.3)
        3. Score based on Proximity (Time until service)
        """
        appointments = await self.appointment_service.get_all_appointments()
        
        # Filter eligible appointments
        candidates = [
            app for app in appointments 
            if app.status == 'pending' and str(app.id) != excluded_appointment_id
        ]
        
        # Calculate scores
        scored_candidates = []
        for app in candidates:
            # Volatility Score
            v_score = 0.3
            if app.volatility_level == VolatilityLevel.HIGH: v_score = 1.0
            elif app.volatility_level == VolatilityLevel.MEDIUM: v_score = 0.6
            
            # Simple scoring for now (can be enhanced)
            final_score = v_score
            scored_candidates.append((final_score, app))
            
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        recommendations = [item[1] for item in scored_candidates[:Config.DEFAULT_RECOMMENDATION_COUNT]]
        
        return {
            "recommendations": recommendations,
            "reasoning": "Based on customer flexibility and schedule optimization."
        }