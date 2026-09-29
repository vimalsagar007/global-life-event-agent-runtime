from typing import Dict, Any


EXCHANGE_RATES: Dict[str, float] = {
    "USD": 1.0,
    "CAD": 1.35,
    "GBP": 0.79,
    "EUR": 0.92,
    "JPY": 150.5,
    "SGD": 1.34,
    "BRL": 4.95,
    "AED": 3.67,
    "AUD": 1.52,
    "INR": 83.1,
}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "hi": "Hindi",
    "te": "Telugu",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "zh": "Mandarin Chinese"
}


class LocalizationEngine:
    """Handles localization calculations, currency conversion, and multi-language summary wrappers."""

    @staticmethod
    def convert_currency(amount: float, from_curr: str, to_curr: str) -> float:
        from_rate = EXCHANGE_RATES.get(from_curr.upper(), 1.0)
        to_rate = EXCHANGE_RATES.get(to_curr.upper(), 1.0)
        usd_amount = amount / from_rate
        return round(usd_amount * to_rate, 2)

    @staticmethod
    def format_currency(amount: float, currency_code: str) -> str:
        code = currency_code.upper()
        symbols = {
            "USD": "$", "CAD": "CA$", "GBP": "£", "EUR": "€",
            "JPY": "¥", "SGD": "S$", "BRL": "R$", "AED": "AED ",
            "AUD": "A$", "INR": "₹"
        }
        symbol = symbols.get(code, f"{code} ")
        return f"{symbol}{amount:,.2f}"

    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        return SUPPORTED_LANGUAGES
