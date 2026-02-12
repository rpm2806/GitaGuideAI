import re
import logging

logger = logging.getLogger(__name__)

class SafetyLayer:
    def __init__(self):
        # Rule 7: Ethical handling for mental-health contexts
        self.self_harm_patterns = [
            r"(?i)\b(kill myself|suicide|end my life|want to die|hurt myself)\b",
            r"(?i)\b(cutting myself|overdose)\b"
        ]
        self.crisis_resources = (
            "I hear your pain, and I want you to be safe. "
            "Please reach out to a professional immediately. "
            "You can call or text 988 in the US/Canada, or contact your local emergency services."
        )

    async def check_input(self, text: str) -> dict:
        """
        Checks input for safety violations.
        Returns a dict with 'safe': bool, 'message': str (if unsafe).
        """
        for pattern in self.self_harm_patterns:
            if re.search(pattern, text):
                logger.warning(f"Safety trigger detected: {pattern}")
                return {"safe": False, "message": self.crisis_resources}
        
        return {"safe": True, "message": None}

    def sanitize(self, text: str) -> str:
        """Basic sanitization to remove potential HTML/scripts."""
        # Simple strip of <script> tags or similar if needed, 
        # though LLMs usually handle raw text fine. 
        # For now, just removing null bytes or control chars could be enough.
        return text.replace("\0", "")
