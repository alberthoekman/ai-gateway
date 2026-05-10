"""
AI Service Module
Handles integration with LLM providers (OpenAI, with fallback to mock)
Supports both free-tier API usage and local testing without API keys.
"""

from typing import Optional


class AIService:
    """
    Unified AI service that supports OpenAI API or mock responses.
    Automatically falls back to mock mode if no API key is provided.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the AI service.

        Args:
            api_key: OpenAI API key (optional - uses mock if None)
            model: OpenAI model to use (default: gpt-3.5-turbo for cost efficiency)
        """
        self.api_key = api_key
        self.model = model
        self.use_openai = api_key is not None

        if self.use_openai:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                print(f"[OK] OpenAI API initialized with model: {model}")
            except ImportError:
                print("[WARNING] OpenAI package not installed. Falling back to mock mode.")
                print("         Install with: pip install openai")
                self.use_openai = False
            except Exception as e:
                print(f"[WARNING] Failed to initialize OpenAI: {e}")
                print("         Falling back to mock mode.")
                self.use_openai = False
        else:
            print("[INFO] No API key provided. Using mock AI mode.")
            print("       Set OPENAI_API_KEY environment variable to enable real AI.")

    def analyze(self, text: str) -> str:
        """
        Analyze text using OpenAI API or mock service.

        Args:
            text: The sanitized input text (PII already removed)

        Returns:
            AI analysis result as markdown-formatted string
        """
        if self.use_openai:
            return self._analyze_with_openai(text)
        else:
            return self._analyze_with_mock(text)

    def get_service_info(self) -> dict:
        """
        Get information about the current AI service configuration.

        Returns:
            Dictionary with service details
        """
        return {
            "provider": "OpenAI" if self.use_openai else "Mock",
            "model": self.model if self.use_openai else "Mock AI",
            "api_configured": self.use_openai,
            "status": "active" if self.use_openai else "mock_mode"
        }

    def _analyze_with_openai(self, text: str) -> str:
        """
        Analyze text using OpenAI API.

        Args:
            text: The input text

        Returns:
            Formatted AI response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Je bent een behulpzame AI-assistent voor de Nederlandse overheid. "
                            "Geef korte, heldere antwoorden in het Nederlands. "
                            "Analyseer de tekst en geef een beknopte samenvatting of antwoord."
                        )
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=500,  # Keep costs low
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()

            # Format response with metadata
            return (
                f"**AI Analyse (OpenAI {self.model})**\n\n"
                f"{ai_response}\n\n"
                f"---\n"
                f"*Model: {self.model} | "
                f"Tokens gebruikt: {response.usage.total_tokens}*"
            )

        except Exception as e:
            # Log error but don't expose to user
            print(f"[ERROR] OpenAI API Error: {e}")

            # Return graceful error message
            return (
                f"**AI Service Tijdelijk Niet Beschikbaar**\n\n"
                f"Er is een probleem opgetreden bij het verbinden met de AI-service. "
                f"Probeer het later opnieuw.\n\n"
                f"*Foutmelding: {str(e)[:100]}*"
            )

    def _analyze_with_mock(self, text: str) -> str:
        """
        Simulate AI analysis (for testing without API key).

        Args:
            text: The input text

        Returns:
            Mock AI response
        """
        word_count = len(text.split())
        char_count = len(text)

        # Simple sentiment analysis
        positive_words = [
            'goed', 'positief', 'uitstekend', 'mooi', 'geweldig',
            'prettig', 'fantastisch', 'prima', 'fijn', 'blij'
        ]
        negative_words = [
            'slecht', 'negatief', 'probleem', 'fout', 'verkeerd',
            'lastig', 'irritant', 'vervelend', 'teleurstellend'
        ]

        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)

        if positive_score > negative_score:
            sentiment = "positief"
        elif negative_score > positive_score:
            sentiment = "negatief"
        else:
            sentiment = "neutraal"

        # Detect question
        is_question = '?' in text
        text_type = "Vraag" if is_question else "Tekst"

        return (
            f"**AI Analyse (Mock Mode)**\n\n"
            f"**Samenvatting:**\n"
            f"Deze tekst bevat {word_count} woorden en {char_count} karakters. "
            f"Het sentiment is {sentiment}.\n\n"
            f"**Details:**\n"
            f"Type: {text_type}\n"
            f"Woorden: {word_count}\n"
            f"Karakters: {char_count}\n"
            f"Sentiment: {sentiment}\n"
            f"Positieve woorden: {positive_score}\n"
            f"Negatieve woorden: {negative_score}\n\n"
            f"---\n"
            f"*Dit is een **simulatie**. Voor echte AI-analyse, configureer een OpenAI API key.*\n"
            f"*Stel `OPENAI_API_KEY` in als omgevingsvariabele.*"
        )
