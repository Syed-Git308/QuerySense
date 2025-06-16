import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
import json

# Connect to database
DATABASE_URL = 'postgresql://querysense:querysense123@localhost:5432/querysense_ai'
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Load the model
print('Loading embedding model...')
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')

# Test query
query = 'how many employees does engineering have?'
print(f'Testing query: "{query}"')

# Generate query embedding
query_embedding = model.encode(query)
print(f'Query embedding shape: {query_embedding.shape}')

# Get all documents and their embeddings
cur.execute('SELECT id, filename, content, embedding FROM documents')
docs = cur.fetchall()

print(f'\nFound {len(docs)} documents in database')

# Calculate similarities
similarities = []
for doc in docs:
    doc_id, filename, content, embedding_json = doc
    
    # Convert JSON back to numpy array
    doc_embedding = np.array(embedding_json)
    
    # Calculate cosine similarity
    similarity = np.dot(query_embedding, doc_embedding) / (
        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
    )
    
    similarities.append({
        'id': doc_id,
        'filename': filename,
        'similarity': float(similarity),
        'content_preview': content[:100] + '...' if len(content) > 100 else content
    })
    
    print(f'Doc {doc_id} ({filename}): similarity = {similarity:.4f}')

# Sort by similarity
similarities.sort(key=lambda x: x['similarity'], reverse=True)

print(f'\nTop 3 most similar documents:')
for i, sim in enumerate(similarities[:3]):
    print(f'{i+1}. {sim["filename"]} - Similarity: {sim["similarity"]:.4f}')
    print(f'   Content: {sim["content_preview"]}')

# Check what threshold is being used
print(f'\nSimilarity threshold in use: 0.3')
print(f'Documents above threshold: {len([s for s in similarities if s["similarity"] >= 0.3])}')

conn.close()
