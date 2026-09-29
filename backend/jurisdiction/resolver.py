import re
import urllib.request
import urllib.parse
import json
import logging
from typing import Tuple, Dict, Any, Optional
from backend.models.domain import Jurisdiction

logger = logging.getLogger("GlobalLifeEventAI")

# In-memory cache for public geocoding requests to respect API rate limits
GEOCODE_CACHE: Dict[str, Jurisdiction] = {}

ISO_COUNTRY_METADATA: Dict[str, Dict[str, Any]] = {
    "in": {"name": "India", "currency": "INR", "language": "hi", "locale": "hi-IN", "timezone": "Asia/Kolkata", "measurement": "metric"},
    "us": {"name": "United States", "currency": "USD", "language": "en", "locale": "en-US", "timezone": "America/New_York", "measurement": "imperial"},
    "gb": {"name": "United Kingdom", "currency": "GBP", "language": "en", "locale": "en-GB", "timezone": "Europe/London", "measurement": "metric"},
    "ca": {"name": "Canada", "currency": "CAD", "language": "en", "locale": "en-CA", "timezone": "America/Toronto", "measurement": "metric"},
    "ch": {"name": "Switzerland", "currency": "CHF", "language": "de", "locale": "de-CH", "timezone": "Europe/Zurich", "measurement": "metric"},
    "de": {"name": "Germany", "currency": "EUR", "language": "de", "locale": "de-DE", "timezone": "Europe/Berlin", "measurement": "metric"},
    "fr": {"name": "France", "currency": "EUR", "language": "fr", "locale": "fr-FR", "timezone": "Europe/Paris", "measurement": "metric"},
    "jp": {"name": "Japan", "currency": "JPY", "language": "ja", "locale": "ja-JP", "timezone": "Asia/Tokyo", "measurement": "metric"},
    "sg": {"name": "Singapore", "currency": "SGD", "language": "en", "locale": "en-SG", "timezone": "Asia/Singapore", "measurement": "metric"},
    "au": {"name": "Australia", "currency": "AUD", "language": "en", "locale": "en-AU", "timezone": "Australia/Sydney", "measurement": "metric"},
    "nz": {"name": "New Zealand", "currency": "NZD", "language": "en", "locale": "en-NZ", "timezone": "Pacific/Auckland", "measurement": "metric"},
    "br": {"name": "Brazil", "currency": "BRL", "language": "pt", "locale": "pt-BR", "timezone": "America/Sao_Paulo", "measurement": "metric"},
    "mx": {"name": "Mexico", "currency": "MXN", "language": "es", "locale": "es-MX", "timezone": "America/Mexico_City", "measurement": "metric"},
    "ae": {"name": "United Arab Emirates", "currency": "AED", "language": "ar", "locale": "ar-AE", "timezone": "Asia/Dubai", "measurement": "metric"},
    "es": {"name": "Spain", "currency": "EUR", "language": "es", "locale": "es-ES", "timezone": "Europe/Madrid", "measurement": "metric"},
    "it": {"name": "Italy", "currency": "EUR", "language": "it", "locale": "it-IT", "timezone": "Europe/Rome", "measurement": "metric"},
    "nl": {"name": "Netherlands", "currency": "EUR", "language": "nl", "locale": "nl-NL", "timezone": "Europe/Amsterdam", "measurement": "metric"},
    "se": {"name": "Sweden", "currency": "SEK", "language": "sv", "locale": "sv-SE", "timezone": "Europe/Stockholm", "measurement": "metric"},
    "no": {"name": "Norway", "currency": "NOK", "language": "no", "locale": "no-NO", "timezone": "Europe/Oslo", "measurement": "metric"},
    "dk": {"name": "Denmark", "currency": "DKK", "language": "da", "locale": "da-DK", "timezone": "Europe/Copenhagen", "measurement": "metric"},
    "fi": {"name": "Finland", "currency": "EUR", "language": "fi", "locale": "fi-FI", "timezone": "Europe/Helsinki", "measurement": "metric"},
    "cn": {"name": "China", "currency": "CNY", "language": "zh", "locale": "zh-CN", "timezone": "Asia/Shanghai", "measurement": "metric"},
    "hk": {"name": "Hong Kong", "currency": "HKD", "language": "zh", "locale": "zh-HK", "timezone": "Asia/Hong_Kong", "measurement": "metric"},
    "kr": {"name": "South Korea", "currency": "KRW", "language": "ko", "locale": "ko-KR", "timezone": "Asia/Seoul", "measurement": "metric"},
    "za": {"name": "South Africa", "currency": "ZAR", "language": "en", "locale": "en-ZA", "timezone": "Africa/Johannesburg", "measurement": "metric"},
    "th": {"name": "Thailand", "currency": "THB", "language": "th", "locale": "th-TH", "timezone": "Asia/Bangkok", "measurement": "metric"},
    "my": {"name": "Malaysia", "currency": "MYR", "language": "ms", "locale": "ms-MY", "timezone": "Asia/Kuala_Lumpur", "measurement": "metric"},
    "ng": {"name": "Nigeria", "currency": "NGN", "language": "en", "locale": "en-NG", "timezone": "Africa/Lagos", "measurement": "metric"},
    "ke": {"name": "Kenya", "currency": "KES", "language": "en", "locale": "en-KE", "timezone": "Africa/Nairobi", "measurement": "metric"},
    "ar": {"name": "Argentina", "currency": "ARS", "language": "es", "locale": "es-AR", "timezone": "America/Buenos_Aires", "measurement": "metric"},
    "sa": {"name": "Saudi Arabia", "currency": "SAR", "language": "ar", "locale": "ar-SA", "timezone": "Asia/Riyadh", "measurement": "metric"},
    "pt": {"name": "Portugal", "currency": "EUR", "language": "pt", "locale": "pt-PT", "timezone": "Europe/Lisbon", "measurement": "metric"},
}

COUNTRY_ALIASES: Dict[str, str] = {
    "uk": "United Kingdom",
    "usa": "United States",
    "us": "United States",
    "uae": "United Arab Emirates",
    "canada": "Canada",
    "india": "India",
    "japan": "Japan",
    "singapore": "Singapore",
    "switzerland": "Switzerland",
    "germany": "Germany",
    "france": "France",
    "brazil": "Brazil",
    "australia": "Australia",
    "portugal": "Portugal",
    "south korea": "South Korea",
    "korea": "South Korea",
    "hong kong": "Hong Kong",
    "china": "China",
    "thailand": "Thailand",
    "malaysia": "Malaysia",
    "saudi arabia": "Saudi Arabia",
    "mexico": "Mexico",
    "argentina": "Argentina",
    "kenya": "Kenya",
    "nigeria": "Nigeria",
    "south africa": "South Africa",
    "new zealand": "New Zealand",
    "netherlands": "Netherlands",
    "italy": "Italy", "spain": "Spain", "sweden": "Sweden", "norway": "Norway", "denmark": "Denmark", "finland": "Finland"
}

KNOWN_CITY_TO_COUNTRY: Dict[str, Tuple[str, str]] = {
    "new york": ("United States", "New York"),
    "nyc": ("United States", "New York"),
    "san francisco": ("United States", "California"),
    "los angeles": ("United States", "California"),
    "chicago": ("United States", "Illinois"),
    "seattle": ("United States", "Washington"),
    "austin": ("United States", "Texas"),
    "boston": ("United States", "Massachusetts"),
    "toronto": ("Canada", "Ontario"),
    "vancouver": ("Canada", "British Columbia"),
    "montreal": ("Canada", "Quebec"),
    "london": ("United Kingdom", "England"),
    "manchester": ("United Kingdom", "England"),
    "edinburgh": ("United Kingdom", "Scotland"),
    "bangalore": ("India", "Karnataka"),
    "bengaluru": ("India", "Karnataka"),
    "hyderabad": ("India", "Telangana"),
    "mumbai": ("India", "Maharashtra"),
    "delhi": ("India", "Delhi"),
    "new delhi": ("India", "Delhi"),
    "chennai": ("India", "Tamil Nadu"),
    "tokyo": ("Japan", "Tokyo"),
    "kyoto": ("Japan", "Kyoto"),
    "osaka": ("Japan", "Osaka"),
    "singapore": ("Singapore", "Central Region"),
    "zurich": ("Switzerland", "Zurich"),
    "geneva": ("Switzerland", "Geneva"),
    "berlin": ("Germany", "Berlin"),
    "munich": ("Germany", "Bavaria"),
    "frankfurt": ("Germany", "Hesse"),
    "paris": ("France", "Île-de-France"),
    "sydney": ("Australia", "New South Wales"),
    "melbourne": ("Australia", "Victoria"),
    "dubai": ("United Arab Emirates", "Dubai"),
    "são paulo": ("Brazil", "São Paulo"),
    "sao paulo": ("Brazil", "São Paulo"),
    "lisbon": ("Portugal", "Lisbon"),
    "seoul": ("South Korea", "Seoul Capital Area"),
    "madrid": ("Spain", "Madrid"),
    "rome": ("Italy", "Lazio"),
    "amsterdam": ("Netherlands", "North Holland"),
    "auckland": ("New Zealand", "Auckland Region"),
    "cape town": ("South Africa", "Western Cape"),
    "lagos": ("Nigeria", "Lagos State"),
    "nairobi": ("Kenya", "Nairobi County"),
    "buenos aires": ("Argentina", "Buenos Aires"),
    "mexico city": ("Mexico", "CDMX"),
    "riyadh": ("Saudi Arabia", "Riyadh Region"),
    "bangkok": ("Thailand", "Bangkok Metropolis"),
    "kuala lumpur": ("Malaysia", "Kuala Lumpur"),
    "hong kong": ("Hong Kong", "Hong Kong"),
    "shanghai": ("China", "Shanghai"),
    "stockholm": ("Sweden", "Stockholm County"),
    "oslo": ("Norway", "Oslo"),
    "copenhagen": ("Denmark", "Capital Region"),
    "helsinki": ("Finland", "Uusimaa")
}


class JurisdictionResolver:
    """Parses text prompts using public OpenStreetMap Geocoding API with multi-stage fallback & caching."""

    @staticmethod
    def geocode_public_api(location_query: str) -> Optional[Jurisdiction]:
        """Calls OpenStreetMap Nominatim Public Geocoding API with caching and failover."""
        clean_query = location_query.strip().lower()
        if not clean_query:
            return None

        # Check Cache
        if clean_query in GEOCODE_CACHE:
            return GEOCODE_CACHE[clean_query]
        
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(location_query.strip())}&format=json&addressdetails=1&accept-language=en"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "GlobalLifeEventAI-Orchestrator/2.0 (contact@globallifeevent.ai)"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if payload and len(payload) > 0:
                    item = payload[0]
                    address = item.get("address", {})
                    country_name = address.get("country") or location_query.strip().title()
                    state_name = address.get("state") or address.get("county") or address.get("region") or country_name
                    city_name = (
                        address.get("city") or 
                        address.get("town") or 
                        address.get("village") or 
                        address.get("municipality") or 
                        address.get("suburb") or 
                        address.get("county") or 
                        location_query.strip().title()
                    )
                    country_code = address.get("country_code", "").lower()

                    meta = ISO_COUNTRY_METADATA.get(country_code, {
                        "name": country_name,
                        "currency": "USD",
                        "language": "en",
                        "locale": f"en-{country_code.upper()}" if country_code else "en-US",
                        "timezone": "UTC",
                        "measurement": "metric"
                    })

                    res = Jurisdiction(
                        country=country_name,
                        region=state_name,
                        city=city_name,
                        postal_code=address.get("postcode"),
                        timezone=meta.get("timezone", "UTC"),
                        currency=meta.get("currency", "USD"),
                        language=meta.get("language", "en"),
                        locale=meta.get("locale", "en-US"),
                        measurement_system=meta.get("measurement", "metric")
                    )
                    GEOCODE_CACHE[clean_query] = res
                    return res
        except Exception as err:
            logger.warning(f"[GEOCODE_API] Public Geocoding API notice for '{location_query}': {err}")
        return None

    @staticmethod
    def resolve_from_text(raw_text: str) -> Tuple[Jurisdiction, Optional[Jurisdiction], bool]:
        text_lower = raw_text.lower()

        # Check for relocation patterns like "from X to Y"
        move_match = re.search(r"(?:from|leaving|out of)\s+([a-z0-9\s,\.-]+?)\s+(?:to|for|into)\s+([a-z0-9\s,\.-]+?)(?:\s+in|\s+with|\s+for|\.|$)", text_lower)
        
        if move_match:
            origin_str = move_match.group(1).strip()
            dest_str = move_match.group(2).strip()
            
            dest_juris = JurisdictionResolver.parse_location_string(dest_str)
            origin_juris = JurisdictionResolver.parse_location_string(
                origin_str, 
                default_country=dest_juris.country if dest_juris else None
            )
            
            is_cross_border = (origin_juris.country.lower() != dest_juris.country.lower())
            return origin_juris, dest_juris, is_cross_border

        # Single location event
        origin_juris = JurisdictionResolver.parse_location_string(text_lower)
        return origin_juris, None, False

    @staticmethod
    def parse_location_string(location_str: str, default_country: Optional[str] = None) -> Jurisdiction:
        if not location_str or not location_str.strip():
            title = default_country or "Local Jurisdiction"
            return Jurisdiction(
                country=title, region=title, city=title,
                postal_code=None, timezone="UTC", currency="USD",
                language="en", locale="en-US", measurement_system="metric"
            )

        # 1. Primary Resolution: Public OpenStreetMap Geocoding API
        api_result = JurisdictionResolver.geocode_public_api(location_str)
        if api_result:
            return api_result

        # 2. Dynamic Fallback: Token parsing without hardcoding static defaults
        raw_city = location_str.split(",")[0].strip().title() if "," in location_str else location_str.strip().title()
        extracted_title = raw_city
        location_lower = location_str.lower()
        
        country_title = default_country or extracted_title
        region_title = extracted_title

        # Check known city dictionary in fallback
        for c_token, (c_country, c_region) in KNOWN_CITY_TO_COUNTRY.items():
            if c_token in location_lower:
                country_title = c_country
                region_title = c_region
                break

        # Check country alias in fallback
        for token, c_name in COUNTRY_ALIASES.items():
            if token in location_lower:
                country_title = c_name
                break

        # Lookup ISO metadata if matched country title
        iso_meta = None
        for cc, meta in ISO_COUNTRY_METADATA.items():
            if meta["name"].lower() == country_title.lower():
                iso_meta = meta
                break

        res = Jurisdiction(
            country=country_title,
            region=region_title,
            city=extracted_title,
            postal_code=None,
            timezone=iso_meta["timezone"] if iso_meta else "UTC",
            currency=iso_meta["currency"] if iso_meta else "USD",
            language=iso_meta["language"] if iso_meta else "en",
            locale=iso_meta["locale"] if iso_meta else "en-US",
            measurement_system=iso_meta["measurement"] if iso_meta else "metric"
        )
        GEOCODE_CACHE[location_str.strip().lower()] = res
        return res
