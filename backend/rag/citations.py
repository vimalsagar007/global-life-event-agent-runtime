from typing import List, Dict, Any
from backend.models.domain import AuthoritySource, AuthorityLevel


class CitationValidator:
    """Validates citations, scores source authority, and formats evidence blocks."""

    @staticmethod
    def calculate_authority_score(source: AuthoritySource) -> float:
        scores = {
            AuthorityLevel.OFFICIAL_GOVERNMENT: 1.0,
            AuthorityLevel.REGULATORY: 0.95,
            AuthorityLevel.OFFICIAL_ORGANIZATION: 0.90,
            AuthorityLevel.INSTITUTIONAL: 0.80,
            AuthorityLevel.TRUSTED_SECONDARY: 0.70,
            AuthorityLevel.GENERAL: 0.50,
            AuthorityLevel.UNKNOWN: 0.20
        }
        return scores.get(source.authority_level, 0.5)

    @staticmethod
    def format_citation(source: AuthoritySource) -> Dict[str, Any]:
        return {
            "source_id": source.source_id,
            "title": source.title,
            "url": source.source_url,
            "country": source.country,
            "jurisdiction": source.jurisdiction,
            "authority_level": source.authority_level.value,
            "effective_date": source.effective_date,
            "last_verified": source.last_verified,
            "freshness": "Current" if source.effective_date >= "2025-01-01" else "Needs Review",
            "summary": source.summary
        }
