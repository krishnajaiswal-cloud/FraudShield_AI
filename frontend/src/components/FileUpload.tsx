import React from 'react';
import { Upload, X } from 'lucide-react';
import { Card } from './Common';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  error?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  error,
}) => {
  const [isDragActive, setIsDragActive] = React.useState(false);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.apk')) {
        setSelectedFile(file);
        onFileSelect(file);
      } else {
        alert('Please select a valid APK file');
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.apk')) {
        setSelectedFile(file);
        onFileSelect(file);
      } else {
        alert('Please select a valid APK file');
      }
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <Card
        onClick={handleClick}
        className={`border-2 border-dashed transition-all cursor-pointer ${
          isDragActive
            ? 'border-risk-critical bg-risk-critical/5'
            : 'border-cyber-border hover:border-cyber-border/80'
        } ${selectedFile ? 'bg-cyber-darker' : ''}`}
      >
        <div className="flex flex-col items-center justify-center py-12 gap-4">
          <div className="relative">
            <Upload className={`w-12 h-12 ${
              isDragActive ? 'text-risk-critical' : 'text-gray-400'
            } transition-colors`} />
            {isDragActive && (
              <div className="absolute inset-0 bg-risk-critical/20 blur-lg" />
            )}
          </div>

          {selectedFile ? (
            <div className="text-center">
              <p className="text-white font-semibold">{selectedFile.name}</p>
              <p className="text-gray-400 text-sm">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <>
              <div className="text-center">
                <p className="text-white font-semibold mb-1">
                  {isDragActive ? 'Drop your APK here' : 'Drag and drop your APK file'}
                </p>
                <p className="text-gray-400 text-sm">or click to browse</p>
              </div>
            </>
          )}
        </div>
      </Card>

      <input
        ref={fileInputRef}
        type="file"
        accept=".apk"
        onChange={handleChange}
        className="hidden"
      />

      {error && (
        <div className="mt-4 p-4 bg-risk-critical/10 border border-risk-critical rounded-lg flex items-start gap-3">
          <X className="w-5 h-5 text-risk-critical flex-shrink-0 mt-0.5" />
          <p className="text-risk-critical text-sm">{error}</p>
        </div>
      )}

      {selectedFile && (
        <button
          onClick={() => setSelectedFile(null)}
          className="mt-4 w-full px-4 py-2 bg-cyber-darker text-gray-300 rounded-lg hover:bg-cyber-border transition-colors"
        >
          Clear Selection
        </button>
      )}
    </div>
  );
};
