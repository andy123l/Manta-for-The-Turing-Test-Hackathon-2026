"""
Sentiment Analyzer for Manta trading agent.
Analyzes news and social media sentiment for crypto markets.
"""

from typing import Dict, List
from datetime import datetime
from transformers import pipeline
import requests
from loguru import logger


class SentimentAnalyzer:
    """
    Analyzes market sentiment from news and social media.

    Uses:
    - Pre-trained NLP models for sentiment analysis
    - Fear & Greed Index
    - News aggregation
    """

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize sentiment analyzer.

        Args:
            model_name: HuggingFace model name for sentiment analysis
        """
        self.model_name = model_name

        # Load sentiment analysis pipeline
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                max_length=512,
                truncation=True
            )
            logger.info("Sentiment model loaded", model=model_name)
        except Exception as e:
            logger.warning("Failed to load sentiment model, using fallback", error=str(e))
            self.sentiment_pipeline = None

        # Crypto-specific keywords
        self.bullish_keywords = [
            "bullish", "moon", "pump", "breakout", "rally", "surge",
            "adoption", "partnership", "institutional", "etf approved",
            "all-time high", "accumulate", "hodl"
        ]

        self.bearish_keywords = [
            "bearish", "crash", "dump", "selloff", "regulation",
            "ban", "hack", "exploit", "scam", "fraud", "panic",
            "capitulation", "liquidation"
        ]

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment score and label
        """
        try:
            if self.sentiment_pipeline:
                result = self.sentiment_pipeline(text[:512])[0]

                # Convert to score (-1 to 1)
                if result["label"] == "POSITIVE":
                    score = result["score"]
                else:
                    score = -result["score"]

                return {
                    "score": score,
                    "label": result["label"],
                    "confidence": result["score"]
                }
            else:
                # Fallback: keyword-based analysis
                return self._keyword_analysis(text)

        except Exception as e:
            logger.error("Error analyzing sentiment", error=str(e))
            return {"score": 0, "label": "NEUTRAL", "confidence": 0}

    def _keyword_analysis(self, text: str) -> Dict:
        """
        Simple keyword-based sentiment analysis.

        Args:
            text: Text to analyze

        Returns:
            Sentiment score
        """
        text_lower = text.lower()

        bullish_count = sum(1 for word in self.bullish_keywords if word in text_lower)
        bearish_count = sum(1 for word in self.bearish_keywords if word in text_lower)

        total = bullish_count + bearish_count
        if total == 0:
            return {"score": 0, "label": "NEUTRAL", "confidence": 0.5}

        score = (bullish_count - bearish_count) / total

        return {
            "score": score,
            "label": "POSITIVE" if score > 0 else "NEGATIVE",
            "confidence": abs(score)
        }

    async def get_crypto_news(self) -> List[Dict]:
        """
        Get latest crypto news from free APIs.

        Returns:
            List of news articles with sentiment
        """
        try:
            # Use CryptoPanic API (free tier)
            url = "https://cryptopanic.com/api/free/v1/posts/"
            params = {
                "auth_token": "",  # Add your token for more results
                "kind": "news",
                "filter": "hot"
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                news = []

                for item in data.get("results", [])[:10]:
                    sentiment = self.analyze_sentiment(item.get("title", ""))
                    news.append({
                        "title": item.get("title"),
                        "source": item.get("source", {}).get("title"),
                        "published": item.get("published_at"),
                        "sentiment": sentiment
                    })

                logger.info("Got crypto news", count=len(news))
                return news
            else:
                logger.warning("Failed to fetch news", status=response.status_code)
                return self._get_mock_news()

        except Exception as e:
            logger.error("Error fetching news", error=str(e))
            return self._get_mock_news()

    def _get_mock_news(self) -> List[Dict]:
        """Get mock news data for testing."""
        return [
            {
                "title": "Bitcoin ETF sees record inflows as institutional adoption grows",
                "source": "CryptoNews",
                "published": datetime.now().isoformat(),
                "sentiment": {"score": 0.8, "label": "POSITIVE", "confidence": 0.85}
            },
            {
                "title": "Crypto market faces regulatory uncertainty in major economies",
                "source": "BlockchainTimes",
                "published": datetime.now().isoformat(),
                "sentiment": {"score": -0.6, "label": "NEGATIVE", "confidence": 0.7}
            },
            {
                "title": "Ethereum completes major network upgrade successfully",
                "source": "EthNews",
                "published": datetime.now().isoformat(),
                "sentiment": {"score": 0.9, "label": "POSITIVE", "confidence": 0.92}
            }
        ]

    async def get_market_sentiment(self) -> Dict:
        """
        Get comprehensive market sentiment.

        Returns:
            Dictionary with overall sentiment score
        """
        try:
            news = await self.get_crypto_news()

            if not news:
                return {"score": 0, "interpretation": "neutral", "news_count": 0}

            # Calculate average sentiment
            scores = [item["sentiment"]["score"] for item in news]
            avg_score = sum(scores) / len(scores) if scores else 0

            # Count bullish vs bearish
            bullish = sum(1 for s in scores if s > 0.2)
            bearish = sum(1 for s in scores if s < -0.2)
            neutral = len(scores) - bullish - bearish

            # Determine interpretation
            if avg_score > 0.3:
                interpretation = "bullish"
            elif avg_score < -0.3:
                interpretation = "bearish"
            else:
                interpretation = "neutral"

            return {
                "score": avg_score,
                "interpretation": interpretation,
                "news_count": len(news),
                "distribution": {
                    "bullish": bullish,
                    "bearish": bearish,
                    "neutral": neutral
                },
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error("Error getting market sentiment", error=str(e))
            return {"score": 0, "interpretation": "neutral", "news_count": 0}

    def get_fear_greed_index(self) -> Dict:
        """
        Get Fear & Greed Index from alternative.me.

        Returns:
            Dictionary with index value and interpretation
        """
        try:
            url = "https://api.alternative.me/fng/"
            params = {"limit": 1}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    entry = data["data"][0]
                    value = int(entry["value"])
                    classification = entry["value_classification"]

                    return {
                        "value": value,
                        "classification": classification,
                        "timestamp": datetime.fromtimestamp(int(entry["timestamp"]))
                    }

            # Fallback to mock data
            return {
                "value": 50,
                "classification": "Neutral",
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error("Error fetching Fear & Greed Index", error=str(e))
            return {
                "value": 50,
                "classification": "Neutral",
                "timestamp": datetime.now()
            }

    def analyze_text_batch(self, texts: List[str]) -> Dict:
        """
        Analyze sentiment of multiple texts.

        Args:
            texts: List of texts to analyze

        Returns:
            Aggregated sentiment analysis
        """
        results = [self.analyze_sentiment(text) for text in texts]

        scores = [r["score"] for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "average_score": avg_score,
            "individual_results": results,
            "count": len(texts)
        }
