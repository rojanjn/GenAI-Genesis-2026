"""
Similarity Search Module

Performs semantic similarity calculations and retrieves similar entries.
Implements cosine similarity for comparing embedding vectors.

Role in system:
- Core logic for finding semantically similar past entries
- Used by the AI journaling companion to retrieve relevant context
- Operates on embedding vectors from OpenAI
"""

import math
from typing import List, Dict, Any, Tuple


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Cosine similarity measures the angle between vectors, ranging from -1 to 1.
    Higher values (closer to 1) indicate more similar vectors.
    
    Args:
        vec1: First vector as list of floats
        vec2: Second vector as list of floats
        
    Returns:
        Similarity score between -1 and 1
        
    Raises:
        ValueError: If vectors have different lengths or are empty
    """
    if not vec1 or not vec2:
        raise ValueError("Vectors cannot be empty")
    
    if len(vec1) != len(vec2):
        raise ValueError(f"Vector dimension mismatch: {len(vec1)} vs {len(vec2)}")
    
    # Compute dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Compute magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    # Compute cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    return similarity


def find_similar_entries(
    new_embedding: List[float],
    entries: List[Dict[str, Any]],
    top_k: int = 3,
) -> List[Tuple[float, Dict[str, Any]]]:
    """
    Find most similar entries based on embedding vectors.
    
    Computes cosine similarity between the new embedding and all entry embeddings.
    Returns top_k most similar entries sorted by similarity descending.
    
    Args:
        new_embedding: Embedding vector of current/new entry
        entries: List of entry dictionaries containing "embedding" field
        top_k: Number of top similar entries to return
        
    Returns:
        List of tuples (similarity_score, entry) sorted by similarity descending
        Only includes entries that have valid embeddings
    """
    similarities: List[Tuple[float, Dict[str, Any]]] = []
    
    for entry in entries:
        # Skip entries without embeddings
        if "embedding" not in entry or not entry["embedding"]:
            continue
        
        try:
            sim = cosine_similarity(new_embedding, entry["embedding"])
            similarities.append((sim, entry))
        except ValueError:
            # Skip entries with invalid embeddings
            continue
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    # Return top_k results
    return similarities[:top_k]


if __name__ == "__main__":
    # Test similarity calculation
    try:
        # Create sample embeddings (5-dimensional for testing)
        vec1 = [1.0, 0.0, 0.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0, 0.0, 0.0]  # Identical
        vec3 = [0.0, 1.0, 0.0, 0.0, 0.0]  # Orthogonal
        
        sim_identical = cosine_similarity(vec1, vec2)
        sim_orthogonal = cosine_similarity(vec1, vec3)
        
        print(f"✓ Cosine similarity calculated successfully")
        print(f"  Identical vectors similarity: {sim_identical:.4f} (expected: 1.0)")
        print(f"  Orthogonal vectors similarity: {sim_orthogonal:.4f} (expected: 0.0)")
        
        # Test similarity search
        entries = [
            {"entry_id": "1", "text": "Happy day", "embedding": [1.0, 0.0, 0.0, 0.0, 0.0]},
            {"entry_id": "2", "text": "Sad day", "embedding": [0.0, 1.0, 0.0, 0.0, 0.0]},
            {"entry_id": "3", "text": "Another happy day", "embedding": [0.95, 0.1, 0.0, 0.0, 0.0]},
        ]
        
        query_embedding = [1.0, 0.0, 0.0, 0.0, 0.0]
        similar = find_similar_entries(query_embedding, entries, top_k=2)
        
        print(f"\n✓ Similarity search completed successfully")
        print(f"  Found {len(similar)} similar entries")
        for score, entry in similar:
            print(f"  - {entry['text']}: {score:.4f}")
            
    except Exception as e:
        print(f"✗ Similarity test failed: {e}")