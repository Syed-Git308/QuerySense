import fs from 'fs-extra';
import path from 'path';
import mammoth from 'mammoth';
import XLSX from 'xlsx';
import csv from 'csv-parser';
import { Readable } from 'stream';

class DocumentProcessor {
  constructor() {    this.supportedTypes = {
      'text/plain': this.processTextFile.bind(this),
      'text/markdown': this.processTextFile.bind(this),
      'application/msword': this.processDocFile.bind(this),
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': this.processDocxFile.bind(this),
      'application/vnd.ms-excel': this.processExcelFile.bind(this),
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': this.processExcelFile.bind(this),
      'text/csv': this.processCSVFile.bind(this),
      'application/json': this.processJSONFile.bind(this)
    };
  }

  async processFile(filePath, mimeType, originalName) {
    try {
      // Check by MIME type first
      if (this.supportedTypes[mimeType]) {
        return await this.supportedTypes[mimeType](filePath, originalName);
      }      // Fallback to file extension
      const ext = path.extname(originalName).toLowerCase();
      switch (ext) {
        case '.txt':
        case '.md':
          return await this.processTextFile(filePath, originalName);
        case '.doc':
          return await this.processDocFile(filePath, originalName);
        case '.docx':
          return await this.processDocxFile(filePath, originalName);
        case '.xls':
        case '.xlsx':
          return await this.processExcelFile(filePath, originalName);
        case '.csv':
          return await this.processCSVFile(filePath, originalName);
        case '.json':
          return await this.processJSONFile(filePath, originalName);
        default:
          throw new Error(`Unsupported file type: ${ext}. PDF support coming in Phase 2!`);
      }
    } catch (error) {
      console.error(`Error processing file ${originalName}:`, error);
      throw new Error(`Failed to process ${originalName}: ${error.message}`);
    }
  }

  async processTextFile(filePath, originalName) {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      return this.cleanText(content);
    } catch (error) {
      throw new Error(`Failed to read text file: ${error.message}`);
    }
  }
  async processPDF(filePath, originalName) {
    throw new Error('PDF support is coming in Phase 2! Please use TXT, DOCX, CSV, XLS, or JSON files for now.');
  }

  async processDocFile(filePath, originalName) {
    throw new Error('Legacy .doc files are not supported in this version. Please convert to .docx format.');
  }

  async processDocxFile(filePath, originalName) {
    try {
      const result = await mammoth.extractRawText({ path: filePath });
      if (result.messages.length > 0) {
        console.warn('Mammoth warnings for', originalName, ':', result.messages);
      }
      return this.cleanText(result.value);
    } catch (error) {
      throw new Error(`Failed to parse DOCX: ${error.message}`);
    }
  }

  async processExcelFile(filePath, originalName) {
    try {
      const workbook = XLSX.readFile(filePath);
      let allText = '';
      
      // Process all sheets
      workbook.SheetNames.forEach(sheetName => {
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        
        // Add sheet name as context
        allText += `\\n\\n=== Sheet: ${sheetName} ===\\n`;
        
        // Convert rows to text
        jsonData.forEach((row, rowIndex) => {
          if (row.length > 0) {
            const rowText = row.map(cell => 
              cell !== null && cell !== undefined ? String(cell).trim() : ''
            ).filter(cell => cell.length > 0).join(' | ');
            
            if (rowText.length > 0) {
              allText += `Row ${rowIndex + 1}: ${rowText}\\n`;
            }
          }
        });
      });

      return this.cleanText(allText);
    } catch (error) {
      throw new Error(`Failed to parse Excel file: ${error.message}`);
    }
  }

  async processCSVFile(filePath, originalName) {
    try {
      const csvData = [];
      const fileContent = await fs.readFile(filePath, 'utf-8');
      
      return new Promise((resolve, reject) => {
        const stream = Readable.from([fileContent]);
        
        stream
          .pipe(csv())
          .on('data', (row) => {
            csvData.push(row);
          })
          .on('end', () => {
            try {
              let text = '';
              
              // Add headers if available
              if (csvData.length > 0) {
                const headers = Object.keys(csvData[0]);
                text += `Headers: ${headers.join(' | ')}\\n\\n`;
                
                // Add each row
                csvData.forEach((row, index) => {
                  const rowText = headers.map(header => 
                    row[header] !== null && row[header] !== undefined ? String(row[header]).trim() : ''
                  ).filter(cell => cell.length > 0).join(' | ');
                  
                  if (rowText.length > 0) {
                    text += `Row ${index + 1}: ${rowText}\\n`;
                  }
                });
              }
              
              resolve(this.cleanText(text));
            } catch (error) {
              reject(new Error(`Failed to process CSV data: ${error.message}`));
            }
          })
          .on('error', (error) => {
            reject(new Error(`Failed to parse CSV: ${error.message}`));
          });
      });
    } catch (error) {
      throw new Error(`Failed to read CSV file: ${error.message}`);
    }
  }

  async processJSONFile(filePath, originalName) {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      const jsonData = JSON.parse(content);
      
      // Convert JSON to searchable text
      const text = this.jsonToText(jsonData);
      return this.cleanText(text);
    } catch (error) {
      throw new Error(`Failed to parse JSON: ${error.message}`);
    }
  }

  jsonToText(obj, prefix = '') {
    let text = '';
    
    if (Array.isArray(obj)) {
      obj.forEach((item, index) => {
        text += `${prefix}[${index}]: ${this.jsonToText(item, prefix + '  ')}\\n`;
      });
    } else if (typeof obj === 'object' && obj !== null) {
      Object.entries(obj).forEach(([key, value]) => {
        if (typeof value === 'object') {
          text += `${prefix}${key}:\\n${this.jsonToText(value, prefix + '  ')}`;
        } else {
          text += `${prefix}${key}: ${String(value)}\\n`;
        }
      });
    } else {
      text += String(obj);
    }
    
    return text;
  }

  cleanText(text) {
    if (!text) return '';
    
    return text
      // Normalize whitespace
      .replace(/\\s+/g, ' ')
      // Remove excessive newlines
      .replace(/\\n\\s*\\n\\s*\\n+/g, '\\n\\n')
      // Trim
      .trim();
  }
  getSupportedExtensions() {
    return ['.txt', '.md', '.docx', '.xls', '.xlsx', '.csv', '.json'];
  }

  getSupportedMimeTypes() {
    return Object.keys(this.supportedTypes);
  }
}

export default DocumentProcessor;
