import re
from typing import Tuple, Dict, Any


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*:\s*",
    r"you\s+are\s+now\s+a",
    r"override\s+safety\s+guidelines",
    r"bypass\s+security",
    r"reveal\s+secret\s+key",
    r"sudo\s+",
    r"rm\s+-rf"
]

DISCLAIMER_TEXT = (
    "NOTICE: The information provided is generated for planning and educational purposes only. "
    "It does NOT constitute individualized legal, tax, financial, medical, or official immigration advice. "
    "Always verify requirements with official government authorities or certified professionals before acting."
)


class SecurityGuard:
    """Security guardrails for prompt injection screening, PII minimization, and mandatory legal disclaimers."""

    @staticmethod
    def inspect_prompt(text: str) -> Tuple[bool, str]:
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Potential prompt injection detected matching pattern: {pattern}"
        return True, "Passed security inspection"

    @staticmethod
    def sanitize_input(text: str) -> str:
        # Mask SSN / SIN / Credit Cards / Passport numbers if detected
        sanitized = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)
        sanitized = re.sub(r"\b\d{9}\b", "[REDACTED_ID]", sanitized)
        sanitized = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED_CARD]", sanitized)
        return sanitized

    @staticmethod
    def attach_disclaimer(content: Dict[str, Any]) -> Dict[str, Any]:
        content["disclaimer"] = DISCLAIMER_TEXT
        return content
