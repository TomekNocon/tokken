"""Airbnb scraper service for extracting and summarizing reviews."""

import re
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import time

from config import config
from exceptions import RunWareAPIError, ValidationError
from logging_config import get_logger
from utils import generate_id, get_current_timestamp

logger = get_logger(__name__)


class AirbnbScraperService:
    """Service for scraping Airbnb reviews and generating summaries."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,pl;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"macOS"'
        })
    
    def validate_airbnb_url(self, url: str) -> str:
        """Validate and normalize Airbnb URL."""
        if not url:
            raise ValidationError("URL is required")
        
        # Check if it's an Airbnb URL (support international domains)
        airbnb_domains = ['airbnb.com', 'airbnb.pl', 'airbnb.co.uk', 'airbnb.de', 'airbnb.fr', 'airbnb.es', 'airbnb.it', 'airbnb.ca', 'airbnb.com.au']
        if not any(domain in url.lower() for domain in airbnb_domains):
            raise ValidationError("URL must be from an Airbnb domain (airbnb.com, airbnb.pl, etc.)")
        
        # Extract listing ID from URL
        listing_id_match = re.search(r'/rooms/(\d+)', url)
        if not listing_id_match:
            raise ValidationError("Invalid Airbnb listing URL format")
        
        listing_id = listing_id_match.group(1)
        
        # Extract domain from original URL
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
        else:
            domain = 'airbnb.com'  # fallback
        
        # Normalize URL to reviews page while preserving domain
        normalized_url = f"https://www.{domain}/rooms/{listing_id}/reviews"
        logger.info(f"Normalized URL: {normalized_url}")
        
        return normalized_url
    
    async def scrape_reviews(self, url: str, max_pages: int = 5) -> List[Dict[str, str]]:
        """Scrape reviews from Airbnb listing."""
        try:
            logger.info(f"Starting to scrape reviews from: {url}")
            
            reviews = []
            page = 1
            
            while page <= max_pages:
                try:
                    # Construct URL with pagination
                    if page == 1:
                        page_url = url
                    else:
                        page_url = f"{url}?page={page}"
                    
                    logger.info(f"Scraping page {page}: {page_url}")
                    
                    # Make request with delay to be respectful
                    time.sleep(2)
                    response = self.session.get(page_url, timeout=30)
                    
                    if response.status_code != 200:
                        logger.warning(f"Failed to fetch page {page}: {response.status_code}")
                        break
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Debug: Log page structure for troubleshooting
                    if page == 1 and attempt == 0:  # Only on first attempt
                        self._debug_page_content(soup)
                    
                    # Find review elements - Airbnb uses various selectors
                    review_elements = self._find_review_elements(soup)
                    
                    if not review_elements:
                        logger.info(f"No reviews found on page {page}, stopping")
                        break
                    
                    # Extract review data
                    page_reviews = self._extract_reviews_from_elements(review_elements)
                    reviews.extend(page_reviews)
                    
                    logger.info(f"Found {len(page_reviews)} reviews on page {page}")
                    
                    # Check if there are more pages
                    if not self._has_next_page(soup):
                        logger.info("No more pages available")
                        break
                    
                    page += 1
                    
                except Exception as e:
                    logger.error(f"Error scraping page {page}: {e}")
                    break
            
            logger.info(f"Total reviews scraped: {len(reviews)}")
            return reviews
            
        except Exception as e:
            logger.error(f"Error scraping reviews: {e}")
            raise ValidationError(f"Failed to scrape reviews: {str(e)}")
    
    def _find_review_elements(self, soup: BeautifulSoup) -> List:
        """Find review elements using multiple selectors."""
        # Try different selectors that Airbnb might use (updated for 2024)
        selectors = [
            # Modern Airbnb selectors
            '[data-testid="reviews-section"] [data-testid="review-content"]',
            '[data-testid="reviews-section"] .review',
            '[data-review-id]',
            '.review-content',
            '.reviews-section .review',
            '.review-text',
            '[aria-label*="review"]',
            # Additional patterns
            '.c1yo0219',  # Airbnb CSS class pattern
            '.r1are2x1',  # Another common pattern
            '[data-plugin-in-point-id*="REVIEWS"]',
            # Generic review patterns
            '.review',
            '[class*="review"]',
            '[id*="review"]'
        ]
        
        all_elements = []
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                logger.debug(f"Found {len(elements)} elements using selector: {selector}")
                all_elements.extend(elements)
        
        # Remove duplicates
        unique_elements = []
        seen_texts = set()
        
        for element in all_elements:
            text = element.get_text(strip=True)[:100]  # First 100 chars for comparison
            if text not in seen_texts and len(text) > 20:
                unique_elements.append(element)
                seen_texts.add(text)
        
        if unique_elements:
            logger.debug(f"Found {len(unique_elements)} unique review elements")
            return unique_elements
        
        # Enhanced fallback: look for paragraphs with review-like content
        paragraphs = soup.find_all(['p', 'div', 'span'], string=re.compile(r'.{30,}'))
        review_elements = []
        
        for element in paragraphs[:50]:  # Limit search
            text = element.get_text(strip=True)
            if (len(text) > 30 and 
                self._looks_like_review_content(text) and 
                text not in seen_texts):
                review_elements.append(element)
                seen_texts.add(text[:100])
        
        logger.debug(f"Found {len(review_elements)} potential reviews using enhanced fallback")
        return review_elements
    
    def _looks_like_review_content(self, text: str) -> bool:
        """Quick check if text looks like review content."""
        text_lower = text.lower()
        
        # Must have review indicators
        review_words = ['stay', 'host', 'place', 'room', 'location', 'clean', 'recommend']
        has_review_words = any(word in text_lower for word in review_words)
        
        # Must not have technical content
        tech_indicators = ['function', 'window.', 'undefined', 'console.', 'document.']
        has_tech_content = any(tech in text_lower for tech in tech_indicators)
        
        return has_review_words and not has_tech_content
    
    def _debug_page_content(self, soup: BeautifulSoup) -> None:
        """Debug page content to understand structure."""
        try:
            # Log page title
            title = soup.find('title')
            if title:
                logger.info(f"Page title: {title.get_text()}")
            
            # Check for common Airbnb elements
            common_elements = [
                'h1', 'h2', 'h3',
                '[data-testid]',
                '.review',
                '[class*="review"]',
                '[id*="review"]'
            ]
            
            for selector in common_elements:
                elements = soup.select(selector)
                if elements:
                    logger.debug(f"Found {len(elements)} elements with selector: {selector}")
                    # Log first few element texts (truncated)
                    for i, elem in enumerate(elements[:3]):
                        text = elem.get_text(strip=True)[:100]
                        if text:
                            logger.debug(f"  Element {i+1}: {text}")
            
            # Check if page looks like it loaded properly
            body_text = soup.get_text()
            if 'airbnb' not in body_text.lower():
                logger.warning("Page content doesn't seem to be from Airbnb - possible redirect or error")
            
            if len(body_text) < 1000:
                logger.warning(f"Page content is very short ({len(body_text)} chars) - might be blocked or empty")
            
            # Look for signs of JavaScript-heavy content
            scripts = soup.find_all('script')
            logger.debug(f"Found {len(scripts)} script tags")
            
            # Check for review-related text in page
            if 'review' in body_text.lower():
                logger.info("Found 'review' text in page content")
            else:
                logger.warning("No 'review' text found in page - reviews might not be accessible")
                
        except Exception as e:
            logger.error(f"Error in debug logging: {e}")
    
    def _extract_reviews_from_elements(self, elements: List) -> List[Dict[str, str]]:
        """Extract review data from HTML elements."""
        reviews = []
        
        for element in elements:
            try:
                # Extract review text
                review_text = self._extract_review_text(element)
                
                if review_text and len(review_text.strip()) > 20:
                    # Extract reviewer name (optional)
                    reviewer_name = self._extract_reviewer_name(element)
                    
                    # Extract date (optional)
                    review_date = self._extract_review_date(element)
                    
                    review = {
                        'text': review_text.strip(),
                        'reviewer': reviewer_name or 'Anonymous',
                        'date': review_date or 'Unknown'
                    }
                    
                    reviews.append(review)
                    
            except Exception as e:
                logger.debug(f"Error extracting review from element: {e}")
                continue
        
        return reviews
    
    def _extract_review_text(self, element) -> str:
        """Extract review text from element."""
        # Try to get text content
        text = element.get_text(separator=' ', strip=True)
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Filter out JavaScript, HTML artifacts, and other noise
        if self._is_valid_review_text(text):
            return text
        else:
            return ""
    
    def _is_valid_review_text(self, text: str) -> bool:
        """Check if text is a valid review (not JavaScript, HTML, etc.)."""
        if not text or len(text) < 10:
            return False
        
        # Filter out JavaScript and technical content
        js_patterns = [
            r'function\s*\(',
            r'window\.',
            r'addEventListener',
            r'typeof\s+\w+',
            r'undefined',
            r'querySelector',
            r'console\.',
            r'document\.',
            r'JSON\.',
            r'fetch\(',
            r'Promise',
            r'async\s+function',
            r'const\s+\w+\s*=',
            r'let\s+\w+\s*=',
            r'var\s+\w+\s*=',
            r'return\s+\w+',
            r'\.prototype\.',
            r'getElementById',
            r'className',
            r'innerHTML',
            r'addEventListener',
            r'removeEventListener',
            r'setTimeout',
            r'setInterval',
            r'bugsnag',
            r'error.*reporting',
            r'payload.*version',
            r'apiKey.*payloadVersion'
        ]
        
        # Check if text contains JavaScript patterns
        text_lower = text.lower()
        for pattern in js_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # Filter out very long single "words" (likely encoded data)
        words = text.split()
        for word in words:
            if len(word) > 100:  # Very long string without spaces
                return False
        
        # Filter out text that's mostly punctuation or symbols
        alpha_ratio = sum(c.isalpha() for c in text) / len(text)
        if alpha_ratio < 0.3:  # Less than 30% letters
            return False
        
        # Filter out common HTML artifacts
        html_artifacts = [
            'data-testid',
            'aria-label',
            'onclick',
            'onload',
            'href=',
            'src=',
            'class=',
            'id=',
            '<script',
            '</script>',
            '<style',
            '</style>',
            'window.location',
            'document.cookie'
        ]
        
        for artifact in html_artifacts:
            if artifact in text_lower:
                return False
        
        # Look for review-like characteristics
        review_indicators = [
            'stay', 'host', 'place', 'room', 'apartment', 'house',
            'location', 'clean', 'comfortable', 'recommend', 'nice',
            'great', 'good', 'bad', 'excellent', 'perfect', 'love',
            'beautiful', 'amazing', 'wonderful', 'fantastic',
            'helpful', 'friendly', 'responsive', 'communication',
            'check-in', 'checkout', 'neighborhood', 'area'
        ]
        
        # Text should contain at least one review indicator
        has_review_words = any(indicator in text_lower for indicator in review_indicators)
        
        return has_review_words
    
    def _extract_reviewer_name(self, element) -> Optional[str]:
        """Extract reviewer name from element."""
        # Look for name patterns
        name_selectors = [
            '.reviewer-name',
            '[data-testid="reviewer-name"]',
            '.review-author',
            '.user-name'
        ]
        
        for selector in name_selectors:
            name_element = element.select_one(selector)
            if name_element:
                return name_element.get_text(strip=True)
        
        return None
    
    def _extract_review_date(self, element) -> Optional[str]:
        """Extract review date from element."""
        # Look for date patterns
        date_selectors = [
            '.review-date',
            '[data-testid="review-date"]',
            '.date',
            'time'
        ]
        
        for selector in date_selectors:
            date_element = element.select_one(selector)
            if date_element:
                return date_element.get_text(strip=True)
        
        return None
    
    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        """Check if there are more pages of reviews."""
        # Look for pagination indicators
        next_selectors = [
            'a[aria-label*="Next"]',
            '.pagination .next',
            '[data-testid="pagination-next"]',
            'a[href*="page="]'
        ]
        
        for selector in next_selectors:
            if soup.select_one(selector):
                return True
        
        return False
    
    async def summarize_reviews(self, reviews: List[Dict[str, str]]) -> str:
        """Summarize reviews using AI."""
        try:
            if not reviews:
                return "No reviews found to summarize."
            
            # Prepare review text for summarization
            review_texts = [review['text'] for review in reviews[:50]]  # Limit to 50 reviews
            combined_text = '\n\n'.join(review_texts)
            
            # Truncate if too long (keep within API limits)
            if len(combined_text) > 8000:
                combined_text = combined_text[:8000] + "..."
            
            # Create summarization prompt
            prompt = f"""Please analyze these Airbnb reviews and provide a comprehensive summary of the accommodation. Focus on:

1. Overall guest satisfaction
2. Key positive aspects mentioned repeatedly
3. Common concerns or negative feedback
4. Location and neighborhood insights
5. Cleanliness and amenities
6. Host responsiveness and communication
7. Value for money
8. Any recurring themes or patterns

Reviews to analyze:
{combined_text}

Please provide a balanced, objective summary that would help potential guests understand what to expect from this accommodation."""

            # Use RunWare API for text summarization
            if not config.RUNWARE_API_KEY:
                # Fallback to simple summarization
                return self._simple_summarization(reviews)
            
            # Use AI for better summarization
            summary = await self._ai_summarization(prompt)
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing reviews: {e}")
            return self._simple_summarization(reviews)
    
    async def _ai_summarization(self, prompt: str) -> str:
        """Use AI API for review summarization."""
        try:
            headers = {
                "Authorization": f"Bearer {config.RUNWARE_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Simple text completion request (adjust based on actual API)
            payload = {
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            # Note: This is a placeholder - adjust based on actual text API endpoint
            response = requests.post(
                "https://api.runware.ai/v1/text", 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('text', self._simple_summarization([]))
            else:
                logger.warning(f"AI summarization failed: {response.status_code}")
                return self._simple_summarization([])
                
        except Exception as e:
            logger.error(f"AI summarization error: {e}")
            return self._simple_summarization([])
    
    def _simple_summarization(self, reviews: List[Dict[str, str]]) -> str:
        """Simple rule-based summarization as fallback."""
        if not reviews:
            return "No reviews available for this accommodation."
        
        total_reviews = len(reviews)
        
        # Count positive/negative keywords
        positive_keywords = ['great', 'excellent', 'amazing', 'perfect', 'wonderful', 'fantastic', 'loved', 'beautiful', 'clean', 'comfortable', 'recommend']
        negative_keywords = ['bad', 'terrible', 'awful', 'dirty', 'uncomfortable', 'noisy', 'disappointed', 'problems', 'issues']
        
        positive_count = 0
        negative_count = 0
        
        common_themes = {}
        
        for review in reviews:
            text = review['text'].lower()
            
            # Count sentiment
            for keyword in positive_keywords:
                if keyword in text:
                    positive_count += 1
            
            for keyword in negative_keywords:
                if keyword in text:
                    negative_count += 1
            
            # Extract themes
            if 'location' in text:
                common_themes['location'] = common_themes.get('location', 0) + 1
            if 'clean' in text:
                common_themes['cleanliness'] = common_themes.get('cleanliness', 0) + 1
            if 'host' in text:
                common_themes['host'] = common_themes.get('host', 0) + 1
        
        # Generate summary
        sentiment = "positive" if positive_count > negative_count else "mixed" if positive_count == negative_count else "negative"
        
        summary = f"""
**Accommodation Summary** (Based on {total_reviews} reviews)

**Overall Sentiment:** {sentiment.title()}
- Positive mentions: {positive_count}
- Negative mentions: {negative_count}

**Common Themes:**
"""
        
        for theme, count in sorted(common_themes.items(), key=lambda x: x[1], reverse=True):
            summary += f"- {theme.title()}: mentioned in {count} reviews\n"
        
        summary += f"\n**Note:** This is a basic analysis. For detailed insights, please review individual guest comments."
        
        return summary