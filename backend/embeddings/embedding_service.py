"""
Embedding Service Module

Generates vector embeddings for journal entries using OpenAI's API.
Handles all communication with OpenAI embedding models.

Role in system:
- Converts text entries into semantic vectors
- Interface to OpenAI embedding models
- Error handling for API failures and rate limits
"""

import os
from typing import List
import openai
from dotenv import load_dotenv
load_dotenv()


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for input text using OpenAI.
    
    Uses the text-embedding-3-small model for efficiency.
    
    Args:
        text: Input text to embed (journal entry or query)
        
    Returns:
        Embedding as list of floats
        
    Raises:
        ValueError: If OPENAI_API_KEY not set
        RuntimeError: If OpenAI API call fails
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        
        embedding = response.data[0].embedding
        return embedding
        
    except openai.APIError as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {str(e)}")


if __name__ == "__main__":
    # Test embedding generation
    try:
        sample_text = "Today was a great day. I felt accomplished and happy."
        embedding = generate_embedding(sample_text)
        print(f"✓ Embedding generated successfully")
        print(f"  Text: {sample_text}")
        print(f"  Embedding dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"✗ Embedding generation failed: {e}")
