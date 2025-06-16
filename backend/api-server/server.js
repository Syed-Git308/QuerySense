import express from 'express';
import cors from 'cors';
import multer from 'multer';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';

// Document processors
import DocumentProcessor from './src/processors/DocumentProcessor.js';
import SearchEngine from './src/search/SearchEngine.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Create uploads directory
const uploadsDir = path.join(__dirname, 'uploads');
await fs.ensureDir(uploadsDir);

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ 
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Accept various document types
    const allowedTypes = [
      'text/plain',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'text/csv',
      'application/json',
      'text/markdown'
    ];
    
    if (allowedTypes.includes(file.mimetype) || 
        file.originalname.match(/\.(txt|md|csv|json|pdf|doc|docx|xls|xlsx)$/i)) {
      cb(null, true);
    } else {
      cb(new Error('File type not supported'), false);
    }
  }
});

// Initialize processors
const documentProcessor = new DocumentProcessor();
const searchEngine = new SearchEngine();

// Routes

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    message: 'QuerySense API is running',
    documentsCount: searchEngine.getDocumentCount()
  });
});

// Upload documents
app.post('/api/upload', upload.array('files', 10), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files uploaded' });
    }

    const results = [];
    
    for (const file of req.files) {
      try {
        console.log(`Processing file: ${file.originalname}`);
        
        // Process the document
        const content = await documentProcessor.processFile(file.path, file.mimetype, file.originalname);
        
        // Add to search engine
        const documentId = uuidv4();
        searchEngine.addDocument({
          id: documentId,
          filename: file.originalname,
          content: content,
          filePath: file.path,
          mimeType: file.mimetype,
          uploadedAt: new Date().toISOString()
        });

        results.push({
          id: documentId,
          filename: file.originalname,
          size: file.size,
          status: 'completed',
          contentLength: content.length
        });

        console.log(`Successfully processed: ${file.originalname}`);
      } catch (error) {
        console.error(`Error processing ${file.originalname}:`, error);
        results.push({
          filename: file.originalname,
          status: 'error',
          error: error.message
        });
      }
    }

    res.json({ 
      message: 'Files processed',
      results,
      totalDocuments: searchEngine.getDocumentCount()
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Upload failed: ' + error.message });
  }
});

// Search/Query documents
app.post('/api/query', async (req, res) => {
  try {
    const { query, limit = 3 } = req.body;
    
    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: 'Query is required' });
    }

    console.log(`Processing query: "${query}"`);
    const startTime = Date.now();

    // Search for relevant documents
    const results = searchEngine.search(query, parseInt(limit));
    
    const responseTime = Date.now() - startTime;
    
    console.log(`Query completed in ${responseTime}ms, found ${results.length} results`);

    res.json({
      query,
      results,
      responseTime,
      totalDocuments: searchEngine.getDocumentCount()
    });
  } catch (error) {
    console.error('Query error:', error);
    res.status(500).json({ error: 'Query failed: ' + error.message });
  }
});

// Get all documents
app.get('/api/documents', (req, res) => {
  try {
    const documents = searchEngine.getAllDocuments();
    res.json({
      documents: documents.map(doc => ({
        id: doc.id,
        filename: doc.filename,
        uploadedAt: doc.uploadedAt,
        contentLength: doc.content.length
      }))
    });
  } catch (error) {
    console.error('Documents error:', error);
    res.status(500).json({ error: 'Failed to get documents: ' + error.message });
  }
});

// Delete document
app.delete('/api/documents/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const document = searchEngine.getDocument(id);
    
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    // Remove file from filesystem
    try {
      await fs.remove(document.filePath);
    } catch (err) {
      console.warn(`Could not delete file: ${document.filePath}`, err);
    }

    // Remove from search engine
    searchEngine.removeDocument(id);

    res.json({ 
      message: 'Document deleted successfully',
      totalDocuments: searchEngine.getDocumentCount()
    });
  } catch (error) {
    console.error('Delete error:', error);
    res.status(500).json({ error: 'Delete failed: ' + error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: 'File too large. Maximum size is 10MB.' });
    }
  }
  
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 QuerySense API Server running on http://localhost:${PORT}`);
  console.log(`📁 Upload directory: ${uploadsDir}`);
  console.log(`🔍 Ready to process documents and answer queries!`);
});

export default app;
