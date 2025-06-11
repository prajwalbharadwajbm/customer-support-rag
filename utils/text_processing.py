import re
from typing import Optional, List, Tuple

def extract_followup_questions(content: Optional[str]) -> Tuple[str, List[str]]:
    """
    Extracts follow-up questions from content marked with << >>
    
    Args:
        content: String that may contain follow-up questions
        
    Returns:
        Tuple of (content without questions, list of questions)
    """
    if content is None:
        return content, []
    return content.split("<<")[0], re.findall(r"<<([^>>]+)>>", content)

def extract_source_url(citation: str) -> str:
    """
    Extracts the URL from a citation string in the format: (Source: [title](url))
    
    Args:
        citation: String containing the citation
        
    Returns:
        The URL from the citation, or empty string if no match found
    """
    pattern = r'\(Source: \[.*?\]\((.*?)\)\)'
    match = re.search(pattern, citation)
    return match.group(1) if match else ""

def format_docs(docs) -> str:
    """
    Formats a list of documents with their sources into a markdown string
    
    Args:
        docs: List of documents with metadata containing source information
        
    Returns:
        Formatted string with document content and sources
    """
    formatted_docs = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get('source', 'Unknown')
        formatted_docs.append(
            f"**Document {i}**:\n"
            f"{doc.page_content}\n"
            f"(Source: [{source}]({source}))"
        )
    return "\n".join(formatted_docs) 