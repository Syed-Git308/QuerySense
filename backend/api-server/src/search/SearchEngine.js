class SearchEngine {
  constructor() {
    this.documents = new Map();
    this.invertedIndex = new Map();
  }

  addDocument(document) {
    // Store the document
    this.documents.set(document.id, document);
    
    // Index the document for search
    this.indexDocument(document);
    
    console.log(`Indexed document: ${document.filename} (${document.content.length} characters)`);
  }

  indexDocument(document) {
    // Tokenize the content
    const words = this.tokenize(document.content.toLowerCase());
    
    // Add to inverted index
    words.forEach((word, position) => {
      if (!this.invertedIndex.has(word)) {
        this.invertedIndex.set(word, new Map());
      }
      
      const docMap = this.invertedIndex.get(word);
      if (!docMap.has(document.id)) {
        docMap.set(document.id, []);
      }
      
      docMap.get(document.id).push(position);
    });
  }
  tokenize(text) {
    // Simple tokenization - split on non-alphanumeric characters
    return text
      .replace(/[^a-zA-Z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2) // Filter out very short words
      .map(word => word.trim())
      .filter(word => word.length > 0);
  }
  search(query, limit = 3) {
    if (!query || query.trim().length === 0) {
      return [];
    }

    const queryWords = this.tokenize(query.toLowerCase());
    console.log('Query words:', queryWords);
    console.log('Available words in index:', Array.from(this.invertedIndex.keys()).slice(0, 10));
    
    if (queryWords.length === 0) {
      return [];
    }

    // Score documents based on term frequency and proximity
    const documentScores = new Map();

    queryWords.forEach(word => {
      if (this.invertedIndex.has(word)) {
        const docMap = this.invertedIndex.get(word);
        
        docMap.forEach((positions, docId) => {
          if (!documentScores.has(docId)) {
            documentScores.set(docId, {
              score: 0,
              matchedTerms: new Set(),
              termFrequencies: new Map()
            });
          }
          
          const docScore = documentScores.get(docId);
          docScore.matchedTerms.add(word);
          docScore.termFrequencies.set(word, positions.length);
          
          // Simple TF scoring
          docScore.score += positions.length;
        });
      }
    });

    // Convert to array and sort by score
    const results = Array.from(documentScores.entries())
      .map(([docId, scoreData]) => {
        const document = this.documents.get(docId);
        
        // Boost score based on query term coverage
        const termCoverage = scoreData.matchedTerms.size / queryWords.length;
        const finalScore = scoreData.score * (1 + termCoverage);
        
        // Extract relevant snippets
        const snippets = this.extractSnippets(document.content, queryWords, 3);
        
        return {
          document: {
            id: document.id,
            filename: document.filename,
            uploadedAt: document.uploadedAt
          },
          score: finalScore,
          relevance: Math.min(0.95, termCoverage * 0.8 + 0.2), // Confidence score
          matchedTerms: Array.from(scoreData.matchedTerms),
          snippets: snippets
        };
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    return results;
  }

  extractSnippets(content, queryWords, maxSnippets = 3) {
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);
    const snippets = [];
    
    for (const sentence of sentences) {
      const lowerSentence = sentence.toLowerCase();
      let matches = 0;
      
      // Count how many query words appear in this sentence
      queryWords.forEach(word => {
        if (lowerSentence.includes(word)) {
          matches++;
        }
      });
      
      if (matches > 0) {
        // Highlight the matching terms
        let highlightedSentence = sentence.trim();
        queryWords.forEach(word => {
          const regex = new RegExp(`\\\\b${this.escapeRegex(word)}\\\\b`, 'gi');
          highlightedSentence = highlightedSentence.replace(regex, `**$&**`);
        });
        
        snippets.push({
          text: highlightedSentence,
          matches: matches
        });
      }
      
      if (snippets.length >= maxSnippets) {
        break;
      }
    }
    
    // Sort by number of matches and return
    return snippets
      .sort((a, b) => b.matches - a.matches)
      .slice(0, maxSnippets)
      .map(s => s.text);
  }

  escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  }

  removeDocument(documentId) {
    const document = this.documents.get(documentId);
    if (!document) {
      return false;
    }

    // Remove from documents
    this.documents.delete(documentId);
    
    // Remove from inverted index
    this.invertedIndex.forEach((docMap, word) => {
      docMap.delete(documentId);
      if (docMap.size === 0) {
        this.invertedIndex.delete(word);
      }
    });

    console.log(`Removed document: ${document.filename}`);
    return true;
  }

  getDocument(documentId) {
    return this.documents.get(documentId);
  }

  getAllDocuments() {
    return Array.from(this.documents.values());
  }

  getDocumentCount() {
    return this.documents.size;
  }

  getIndexStats() {
    return {
      documentCount: this.documents.size,
      uniqueWords: this.invertedIndex.size,
      totalWords: Array.from(this.invertedIndex.values()).reduce(
        (sum, docMap) => sum + Array.from(docMap.values()).reduce(
          (docSum, positions) => docSum + positions.length, 0
        ), 0
      )
    };
  }
}

export default SearchEngine;
