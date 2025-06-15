import React, { useState, useRef } from 'react';
import { Upload, File, X, CheckCircle } from 'lucide-react';

interface UploadedFile {
  id: string;
  name: string;
  size: string;
  type: string;
  status: 'uploading' | 'completed' | 'error';
}

const UploadPanel: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (fileList: FileList) => {
    const newFiles = Array.from(fileList).map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: formatFileSize(file.size),
      type: file.type || 'unknown',
      status: 'uploading' as const,
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Simulate upload completion
    newFiles.forEach(file => {
      setTimeout(() => {
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'completed' } : f
        ));
      }, 1000 + Math.random() * 2000);
    });
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  return (
    <section className="pt-8 pb-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-4xl font-semibold text-black mb-4 tracking-tight">Knowledge Upload</h2>
          <p className="text-xl text-black/70 font-medium">Upload your documents to expand the knowledge base</p>
        </div>

        {/* Upload Zone */}
        <div
          className={`relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-200 ${
            dragActive
              ? 'border-black/30 bg-black/5 scale-[1.02]'
              : 'border-black/20 bg-white/60 backdrop-blur-sm hover:bg-white/80 hover:shadow-lg'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.md,.doc,.docx"
            onChange={(e) => e.target.files && handleFiles(e.target.files)}
            className="hidden"
          />

          <Upload size={48} strokeWidth={1} className="mx-auto mb-6 text-black/30" />
          <h3 className="text-2xl font-semibold text-black mb-3 tracking-tight">
            Drop files here or click to upload
          </h3>
          <p className="text-black/60 mb-8 font-medium">
            Supports PDF, TXT, MD, DOC, DOCX files up to 10MB each
          </p>

          <button
            onClick={() => inputRef.current?.click()}
            className="inline-flex items-center px-8 py-3 bg-black text-white rounded-full font-medium hover:bg-black/90 transition-all duration-200 hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
          >
            <Upload size={18} strokeWidth={1.5} className="mr-2" />
            Add Files
          </button>
        </div>

        {/* Uploaded Files */}
        {files.length > 0 && (
          <div className="mt-12 bg-white/60 backdrop-blur-sm rounded-2xl border border-black/10 p-8 shadow-sm">
            <h3 className="text-xl font-semibold text-black mb-6 tracking-tight">Uploaded Files</h3>
            <div className="space-y-3">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between p-4 bg-white/80 rounded-xl border border-black/5 hover:shadow-sm transition-all duration-200"
                >
                  <div className="flex items-center space-x-4">
                    <File size={18} strokeWidth={1.5} className="text-black/50" />
                    <div>
                      <p className="font-medium text-black">{file.name}</p>
                      <p className="text-sm text-black/50">{file.size}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {file.status === 'uploading' && (
                      <div className="w-4 h-4 border-2 border-black/20 border-t-black/60 rounded-full animate-spin" />
                    )}
                    {file.status === 'completed' && (
                      <CheckCircle size={18} strokeWidth={1.5} className="text-green-600" />
                    )}
                    <button
                      onClick={() => removeFile(file.id)}
                      className="p-1 text-black/40 hover:text-black/60 hover:bg-black/5 rounded-lg transition-all duration-150"
                    >
                      <X size={14} strokeWidth={1.5} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default UploadPanel;