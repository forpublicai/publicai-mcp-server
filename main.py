# main.py
from fastmcp import FastMCP
from typing import Dict, List
import urllib.request
import json
import sys

mcp = FastMCP("Swiss Voting Assistant")

INITIATIVES_URL = (
    "https://raw.githubusercontent.com/pluzgi/publicai-mcp-server/main/servers/swiss-voting/data/current_initiatives.json"
)


def load_votes() -> dict:
    """Internal helper: Load votes from GitHub-hosted JSON."""
    try:
        with urllib.request.urlopen(INITIATIVES_URL, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"Failed to load data: {e}", "federal_initiatives": []}


@mcp.tool()
def get_upcoming_initiatives() -> dict:
    """Return the entire Swiss voting dataset."""
    try:
        data = load_votes()
        return data
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_vote_by_id(vote_id: str) -> dict:
    """Return metadata for a specific Swiss federal vote by its ID."""
    try:
        data = load_votes()
        for vote in data.get("federal_initiatives", []):
            if vote.get("vote_id") == vote_id:
                return vote
        return {"error": f"No vote found with ID {vote_id}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_brochure_text(vote_id: str, lang: str = "de") -> dict:
    """
    Get the extracted text of the official Swiss voting brochure.
    
    Args:
        vote_id: Swissvotes numeric ID, e.g., "681"
        lang: Language code ("de", "fr", "it")
    
    Returns:
        Dict with brochure text (pre-extracted by GitHub Actions)
    """
    try:
        data = load_votes()
        
        # Find the vote
        vote = None
        for v in data.get("federal_initiatives", []):
            if v.get("vote_id") == vote_id:
                vote = v
                break
        
        if not vote:
            return {"error": f"No vote found with ID {vote_id}"}
        
        # Get pre-extracted brochure texts
        brochure_texts = vote.get("brochure_texts", {})
        
        if not brochure_texts:
            return {
                "error": "No brochure text available",
                "pdf_url": vote.get("abstimmungsbuechlein_pdf", "")
            }
        
        # Return text for requested language
        if lang in brochure_texts:
            return {
                "vote_id": vote_id,
                "language": lang,
                "text": brochure_texts[lang],
                "pdf_url": vote.get("abstimmungsbuechlein_pdf", "")
            }
        else:
            return {
                "error": f"Brochure not available in {lang}",
                "available_languages": list(brochure_texts.keys()),
                "pdf_url": vote.get("abstimmungsbuechlein_pdf", "")
            }
    
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def search_votes_by_keyword(keyword: str) -> list:
    """Search upcoming Swiss votes by keyword in title or policy area."""
    try:
        data = load_votes()
        results = []
        
        for vote in data.get("federal_initiatives", []):
            title = vote.get("offizieller_titel", "").lower()
            policy = vote.get("politikbereich", "").lower()
            
            if keyword.lower() in title or keyword.lower() in policy:
                results.append({
                    "vote_id": vote.get("vote_id"),
                    "title": vote.get("offizieller_titel"),
                    "date": vote.get("abstimmungsdatum"),
                })
        
        return results if results else [{"info": f"No matches found for '{keyword}'"}]
    
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_bbc_news(
    lang: str = "english",
    max_articles: Optional[int] = 10
) -> Dict[str, any]:
    """Get latest news articles from BBC News in various languages.

    Args:
        lang: Language code (e.g., "english", "bengali", "hindi", "arabic", "spanish")
        max_articles: Maximum number of articles to return (default: 10)

    Returns:
        Dictionary with latest BBC news articles including titles, summaries, images, and links
    """
    try:
        url = f"https://bbc-news-api.vercel.app/news?lang={urllib.parse.quote(lang)}"

        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            # Collect all articles from all sections
            all_articles = []

            for key, value in data.items():
                if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                    for article in value:
                        # Skip articles with null titles and summaries
                        if article.get('title') or article.get('summary'):
                            all_articles.append({
                                'title': article.get('title', 'No title'),
                                'summary': article.get('summary', 'No summary'),
                                'image_url': article.get('image_link', ''),
                                'article_url': article.get('news_link', ''),
                                'section': key,
                                'source': 'BBC News'
                            })

            # Limit articles
            all_articles = all_articles[:max_articles]

            return {
                'status': 'success',
                'language': lang,
                'articles_count': len(all_articles),
                'articles': all_articles,
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'api_elapsed_time': data.get('elapsed time', 'N/A')
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}",
                'language': lang
            }
    except urllib.error.HTTPError as e:
        return {
            'status': 'error',
            'error': f"HTTP Error {e.code}: {e.reason}",
            'suggestion': 'Check if the language code is valid. Use get_bbc_languages() to see available languages.'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to fetch BBC news: {str(e)}"
        }

@mcp.tool()
def get_bbc_latest_by_section(
    lang: str = "english"
) -> Dict[str, any]:
    """Get the most recent BBC News organized by sections/categories.

    Args:
        lang: Language code (e.g., "english", "bengali", "hindi", "arabic")

    Returns:
        Dictionary with news organized by sections (e.g., Top Stories, World, Business, etc.)
    """
    try:
        url = f"https://bbc-news-api.vercel.app/latest?lang={urllib.parse.quote(lang)}"

        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            sections = {}
            total_articles = 0

            # Extract all sections (everything except status, elapsed time, timestamp)
            for key, value in data.items():
                if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                    sections[key] = [
                        {
                            'title': article.get('title', ''),
                            'summary': article.get('summary', ''),
                            'image_url': article.get('image_link', ''),
                            'article_url': article.get('news_link', ''),
                            'section': key
                        }
                        for article in value
                    ]
                    total_articles += len(sections[key])

            return {
                'status': 'success',
                'language': lang,
                'total_sections': len(sections),
                'total_articles': total_articles,
                'sections': sections,
                'section_names': list(sections.keys()),
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'api_elapsed_time': data.get('elapsed time', 'N/A'),
                'source': 'BBC News'
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}",
                'language': lang
            }
    except urllib.error.HTTPError as e:
        return {
            'status': 'error',
            'error': f"HTTP Error {e.code}: {e.reason}",
            'suggestion': 'Check if the language code is valid. Use get_bbc_languages() to see available languages.'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to fetch BBC latest news: {str(e)}"
        }

@mcp.tool()
def get_bbc_languages() -> Dict[str, any]:
    """Get a list of all supported languages for BBC News.

    Returns:
        Dictionary with all available BBC News language services, their codes, URLs, and descriptions
    """
    try:
        url = "https://bbc-news-api.vercel.app/languages"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            languages = data.get('languages', [])

            return {
                'status': 'success',
                'total_languages': len(languages),
                'languages': [
                    {
                        'code': lang.get('code', ''),
                        'name': lang.get('name', ''),
                        'url': lang.get('url', ''),
                        'description': lang.get('description', '')
                    }
                    for lang in languages
                ],
                'language_codes': [lang.get('code', '') for lang in languages],
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'usage_note': 'Use the language codes with get_bbc_news() or get_bbc_latest_by_section()'
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}"
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to fetch BBC languages: {str(e)}"
        }

@mcp.tool()
def search_bbc_news_by_topic(
    topic: str,
    lang: str = "english",
    max_results: int = 5
) -> Dict[str, any]:
    """Search BBC News articles for a specific topic or keyword.

    Args:
        topic: Topic or keyword to search for (e.g., "climate", "economy", "technology")
        lang: Language code (default: "english")
        max_results: Maximum number of matching articles to return (default: 5)

    Returns:
        Dictionary with BBC news articles matching the topic
    """
    try:
        # Fetch latest news
        url = f"https://bbc-news-api.vercel.app/news?lang={urllib.parse.quote(lang)}"

        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            # Collect all articles from all sections
            all_articles = []

            for key, value in data.items():
                if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                    for article in value:
                        if article.get('title') or article.get('summary'):
                            all_articles.append({
                                'title': article.get('title', ''),
                                'summary': article.get('summary', ''),
                                'image_link': article.get('image_link', ''),
                                'news_link': article.get('news_link', ''),
                                'section': key
                            })

            # Filter articles by topic (case-insensitive search in title and summary)
            topic_lower = topic.lower()
            matching_articles = []

            for article in all_articles:
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()

                if topic_lower in title or topic_lower in summary:
                    matching_articles.append({
                        'title': article.get('title', ''),
                        'summary': article.get('summary', ''),
                        'image_url': article.get('image_link', ''),
                        'article_url': article.get('news_link', ''),
                        'section': article.get('section', ''),
                        'relevance': 'title match' if topic_lower in title else 'summary match'
                    })

                if len(matching_articles) >= max_results:
                    break

            return {
                'status': 'success',
                'search_topic': topic,
                'language': lang,
                'matches_found': len(matching_articles),
                'articles': matching_articles,
                'searched_articles': len(all_articles),
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note': 'Search performed on latest BBC News articles. For comprehensive search, use BBC website directly.'
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}",
                'language': lang
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to search BBC news: {str(e)}"
        }

@mcp.tool()
def get_bbc_multilingual_headlines(
    languages: Optional[List[str]] = None,
    headlines_per_language: int = 3
) -> Dict[str, any]:
    """Get top headlines from BBC News in multiple languages simultaneously.

    Args:
        languages: List of language codes (e.g., ["english", "hindi", "arabic"]). If None, uses ["english", "spanish", "arabic"]
        headlines_per_language: Number of headlines per language (default: 3)

    Returns:
        Dictionary with top headlines organized by language
    """
    if languages is None:
        languages = ["english", "spanish", "arabic"]

    results = {
        'status': 'success',
        'languages_requested': languages,
        'headlines_by_language': {},
        'total_headlines': 0,
        'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    for lang in languages:
        try:
            url = f"https://bbc-news-api.vercel.app/news?lang={urllib.parse.quote(lang)}"

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode())

            if data.get('status') == 200:
                # Collect all articles from all sections
                all_articles = []

                for key, value in data.items():
                    if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                        for article in value:
                            if article.get('title') or article.get('summary'):
                                all_articles.append({
                                    'title': article.get('title', 'No title'),
                                    'summary': article.get('summary', 'No summary'),
                                    'news_link': article.get('news_link', ''),
                                    'section': key
                                })

                # Limit to requested number
                all_articles = all_articles[:headlines_per_language]

                results['headlines_by_language'][lang] = {
                    'language_name': lang.capitalize(),
                    'headlines': [
                        {
                            'title': article.get('title', ''),
                            'summary': article.get('summary', '')[:150] + '...' if len(article.get('summary', '')) > 150 else article.get('summary', ''),
                            'url': article.get('news_link', ''),
                            'section': article.get('section', '')
                        }
                        for article in all_articles
                    ],
                    'count': len(all_articles)
                }
                results['total_headlines'] += len(all_articles)
            else:
                results['headlines_by_language'][lang] = {
                    'language_name': lang.capitalize(),
                    'error': f"Failed to fetch (status {data.get('status')})",
                    'count': 0
                }
        except Exception as e:
            results['headlines_by_language'][lang] = {
                'language_name': lang.capitalize(),
                'error': str(e),
                'count': 0
            }

    return results

@mcp.tool()
def fact_check_claim(
    claim: str,
    source: Optional[str] = None,
    date_published: Optional[str] = None
) -> Dict[str, any]:
    """Oh Really? - Fact-checking service that provides references for claims made in the news.

    This tool helps verify claims by providing context, related facts, and authoritative sources.
    Particularly useful for BBC and UK news content verification.

    Args:
        claim: The claim or statement to fact-check (e.g., "The UK has the oldest broadcasting service in the world")
        source: Optional source where the claim was made (e.g., "BBC News", "The Guardian")
        date_published: Optional date when claim was published (YYYY-MM-DD format)

    Returns:
        Dictionary with fact-check results, verification status, references, and context
    """
    import random

    # This is a demonstration tool that shows the structure of fact-checking responses
    # In production, this would integrate with real fact-checking databases and APIs

    # Generate a fact-check reference ID
    check_id = f"BBC-FC-{random.randint(100000, 999999)}"

    # Simulate fact-checking logic
    claim_lower = claim.lower()

    # Example fact-checking responses based on common UK/BBC related claims
    fact_checks = {
        'bbc': {
            'verification': 'verified',
            'context': 'The BBC (British Broadcasting Corporation) is indeed one of the oldest and largest broadcasting organizations.',
            'key_facts': [
                'BBC founded in 1922 as British Broadcasting Company',
                'Became British Broadcasting Corporation in 1927',
                'BBC Archives contain material dating back to 1890',
                'Over 15 million items in BBC Archives'
            ],
            'sources': [
                {'title': 'BBC History', 'url': 'https://www.bbc.co.uk/historyofthebbc', 'type': 'official'},
                {'title': 'BBC Written Archives Centre', 'url': 'https://www.bbc.co.uk/archive', 'type': 'official'},
                {'title': 'BBC Royal Charter', 'url': 'https://www.bbc.com/aboutthebbc/governance', 'type': 'official'}
            ]
        },
        'archive': {
            'verification': 'verified',
            'context': 'The BBC Archives are one of the largest broadcast archives in the world.',
            'key_facts': [
                'Over 15 million items on 60 miles of shelving',
                'Approximately 1 million hours of playable media',
                'Television Archive: 1.5M+ tape items, 600K+ film cans',
                'Sound Archive: 700K vinyl records, 180K 78rpm records',
                'Photographic Library: 7 million images dating to 1922'
            ],
            'sources': [
                {'title': 'BBC Archives Wikipedia', 'url': 'https://en.wikipedia.org/wiki/BBC_Archives', 'type': 'reference'},
                {'title': 'BBC Archive Centre', 'url': 'https://www.bbc.co.uk/archive', 'type': 'official'}
            ]
        },
        'television': {
            'verification': 'partially-verified',
            'context': 'BBC Television Service began regular broadcasts in 1936.',
            'key_facts': [
                'BBC Television Service launched November 2, 1936',
                'World\'s first regular high-definition television service',
                'Suspended during WWII (1939-1946)',
                'Earliest archived BBC TV footage dates to 1936'
            ],
            'sources': [
                {'title': 'BBC History of Television', 'url': 'https://www.bbc.co.uk/historyofthebbc/timelines/television', 'type': 'official'},
                {'title': 'British Film Institute', 'url': 'https://www.bfi.org.uk/', 'type': 'archive'}
            ]
        },
        'nhs': {
            'verification': 'verified',
            'context': 'The National Health Service (NHS) provides healthcare to UK residents.',
            'key_facts': [
                'NHS founded on July 5, 1948',
                'Provides healthcare free at point of use',
                'Funded through taxation',
                'One of the largest employers in the world'
            ],
            'sources': [
                {'title': 'NHS Official Website', 'url': 'https://www.nhs.uk/about-us', 'type': 'official'},
                {'title': 'UK Government - NHS', 'url': 'https://www.gov.uk/government/organisations/nhs', 'type': 'government'}
            ]
        },
        'uk government': {
            'verification': 'context-needed',
            'context': 'UK Government claims require specific context and date verification.',
            'key_facts': [
                'UK is a constitutional monarchy with parliamentary democracy',
                'Government data available at gov.uk',
                'Parliamentary records available at parliament.uk',
                'Official statistics from Office for National Statistics (ONS)'
            ],
            'sources': [
                {'title': 'UK Government', 'url': 'https://www.gov.uk', 'type': 'government'},
                {'title': 'UK Parliament', 'url': 'https://www.parliament.uk', 'type': 'government'},
                {'title': 'Office for National Statistics', 'url': 'https://www.ons.gov.uk', 'type': 'statistics'}
            ]
        }
    }

    # Determine which fact-check template to use
    selected_check = None
    for key in fact_checks:
        if key in claim_lower:
            selected_check = fact_checks[key]
            break

    # Default response if no specific match
    if not selected_check:
        selected_check = {
            'verification': 'requires-investigation',
            'context': 'This claim requires further investigation with authoritative sources.',
            'key_facts': [
                'Always verify claims with multiple authoritative sources',
                'Check publication dates and context',
                'Look for primary sources when possible',
                'Consider potential bias in sources'
            ],
            'sources': [
                {'title': 'BBC Reality Check', 'url': 'https://www.bbc.co.uk/news/reality_check', 'type': 'fact-checking'},
                {'title': 'Full Fact UK', 'url': 'https://fullfact.org', 'type': 'fact-checking'},
                {'title': 'UK Government Statistics', 'url': 'https://www.gov.uk/search/research-and-statistics', 'type': 'statistics'}
            ]
        }

    # Build response
    response = {
        'fact_check_id': check_id,
        'claim': claim,
        'verification_status': selected_check['verification'],
        'status_explanation': {
            'verified': 'Claim is supported by authoritative sources',
            'partially-verified': 'Claim is partially accurate but needs context',
            'context-needed': 'Claim requires additional context to verify',
            'requires-investigation': 'Claim needs further investigation',
            'disputed': 'Claim is disputed by authoritative sources',
            'false': 'Claim is contradicted by authoritative sources'
        }.get(selected_check['verification'], 'Status unknown'),
        'context': selected_check['context'],
        'key_facts': selected_check['key_facts'],
        'authoritative_sources': selected_check['sources'],
        'verification_date': datetime.now().strftime('%Y-%m-%d'),
        'source_metadata': {
            'claim_source': source if source else 'Not specified',
            'date_published': date_published if date_published else 'Not specified'
        },
        'bbc_credit': 'Fact-checking powered by BBC-style verification standards',
        'methodology': [
            '1. Identify claim and extract key assertions',
            '2. Search authoritative sources (government, academic, official records)',
            '3. Cross-reference multiple sources',
            '4. Provide context and nuance',
            '5. Cite primary sources where possible'
        ],
        'recommended_actions': {
            'verified': 'Claim appears accurate based on available sources',
            'partially-verified': 'Review additional context before sharing',
            'context-needed': 'Seek more information about specific circumstances',
            'requires-investigation': 'Verify with multiple authoritative sources before accepting',
            'disputed': 'Be aware of conflicting information from reliable sources',
            'false': 'Do not share; claim contradicted by evidence'
        }.get(selected_check['verification'], 'Investigate further'),
        'additional_resources': {
            'uk_fact_checking': [
                'BBC Reality Check',
                'Full Fact',
                'Channel 4 FactCheck'
            ],
            'uk_government_data': [
                'gov.uk/search/research-and-statistics',
                'Office for National Statistics (ONS)',
                'UK Parliament Hansard'
            ],
            'archives': [
                'BBC Archives',
                'British Library',
                'The National Archives'
            ]
        },
        'note': 'DEMO FACT-CHECK - This demonstrates BBC-quality fact-checking methodology. In production, would integrate with real-time fact-checking databases and AI-powered verification.'
    }

    return response

@mcp.tool()
def generate_uk_archive_alt_text(
    image_description: str,
    archive_context: Optional[str] = None,
    date_circa: Optional[str] = None,
    format_type: Optional[str] = None
) -> Dict[str, any]:
    """Generate descriptive alt text for UK archive images (BBC Archives, British Film Institute, National Archives, etc.).

    This tool helps make historical archive materials more accessible by generating comprehensive,
    descriptive alt text that follows archival and accessibility best practices.

    Args:
        image_description: Basic description of what's visible in the image (e.g., "black and white photo of broadcasting equipment")
        archive_context: Optional context about the source (e.g., "BBC Television Archive", "British Film Institute collection")
        date_circa: Optional approximate date or era (e.g., "1936", "1960s", "mid-1950s")
        format_type: Optional original format (e.g., "film still", "publicity photograph", "telerecording", "wax cylinder label")

    Returns:
        Dictionary with generated alt text in various lengths and accessibility compliance information
    """
    # Build comprehensive alt text
    alt_text_parts = []

    # Add format context if provided
    if format_type:
        alt_text_parts.append(format_type.capitalize())

    # Add date context
    if date_circa:
        alt_text_parts.append(f"circa {date_circa}")

    # Add main description
    alt_text_parts.append(image_description)

    # Add archive context
    if archive_context:
        alt_text_parts.append(f"From {archive_context}")

    # Generate different length versions
    full_alt_text = ". ".join(alt_text_parts)

    # Short version (<=125 characters) - WCAG recommended
    short_version = image_description[:120] + "..." if len(image_description) > 125 else image_description

    # Medium version (descriptive but concise)
    medium_parts = [image_description]
    if date_circa:
        medium_parts.append(f"circa {date_circa}")
    medium_version = ". ".join(medium_parts)

    # Generate structured metadata
    metadata = {
        'description': image_description,
        'temporal_context': date_circa if date_circa else 'unknown',
        'format': format_type if format_type else 'photograph',
        'archive_source': archive_context if archive_context else 'UK archives'
    }

    # Accessibility tips based on content
    accessibility_tips = [
        "Alt text should describe the image content, not interpret it",
        "For historical images, include temporal context when known",
        "Avoid starting with 'Image of' or 'Picture of'"
    ]

    if format_type and 'film' in format_type.lower():
        accessibility_tips.append("For film stills, mention if it's a scene or behind-the-scenes")

    return {
        'alt_text_short': short_version,
        'alt_text_medium': medium_version,
        'alt_text_full': full_alt_text,
        'character_count': {
            'short': len(short_version),
            'medium': len(medium_version),
            'full': len(full_alt_text)
        },
        'metadata': metadata,
        'wcag_compliant': len(short_version) <= 125,
        'accessibility_tips': accessibility_tips,
        'example_usage': {
            'html': f'<img src="archive-image.jpg" alt="{medium_version}">',
            'markdown': f'![{medium_version}](archive-image.jpg)',
            'aria_label': medium_version
        },
        'archive_context': {
            'bbc_archives': 'Over 15 million items spanning 1890-present',
            'collections': [
                'BBC Television Archive (1.5M+ tape items)',
                'BBC Sound Archive (700K vinyl, 180K 78rpm records)',
                'BBC Written Archives (1922-present)',
                'BBC Photographic Library (7M images)',
                'Heritage Collection (broadcast technology, props)'
            ],
            'access_note': 'Material being digitized from analogue formats for preservation'
        }
    }

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="http", host="127.0.0.1", port=8000)
    else:
        mcp.run()