import { useState, useCallback } from 'react';
import { Upload, FileAudio, X, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface AudioUploaderProps {
  onFileSelect: (file: File) => void;
}

const ACCEPTED_FORMATS = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/webm'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const MAX_DURATION = 600; // 10 minutes in seconds

export const AudioUploader = ({ onFileSelect }: AudioUploaderProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { toast } = useToast();

  const validateFile = useCallback(async (file: File): Promise<boolean> => {
    // Check file type
    if (!ACCEPTED_FORMATS.includes(file.type)) {
      toast({
        variant: "destructive",
        title: "Invalid file format",
        description: "Please upload WAV, MP3, OGG, or WebM audio files only."
      });
      return false;
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      toast({
        variant: "destructive",
        title: "File too large",
        description: `Maximum file size is ${MAX_FILE_SIZE / 1024 / 1024}MB.`
      });
      return false;
    }

    // Check duration
    const audio = new Audio();
    const url = URL.createObjectURL(file);
    
    return new Promise((resolve) => {
      audio.addEventListener('loadedmetadata', () => {
        URL.revokeObjectURL(url);
        if (audio.duration > MAX_DURATION) {
          toast({
            variant: "destructive",
            title: "Audio too long",
            description: `Maximum duration is ${MAX_DURATION / 60} minutes.`
          });
          resolve(false);
        } else {
          resolve(true);
        }
      });
      
      audio.addEventListener('error', () => {
        URL.revokeObjectURL(url);
        toast({
          variant: "destructive",
          title: "Invalid audio file",
          description: "Could not read the audio file."
        });
        resolve(false);
      });
      
      audio.src = url;
    });
  }, [toast]);

  const handleFile = useCallback(async (file: File) => {
    const isValid = await validateFile(file);
    if (isValid) {
      setSelectedFile(file);
      onFileSelect(file);
      toast({
        title: "File ready",
        description: `${file.name} is ready for processing.`
      });
    }
  }, [validateFile, onFileSelect, toast]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const clearFile = useCallback(() => {
    setSelectedFile(null);
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          relative overflow-hidden rounded-2xl border-2 border-dashed transition-all duration-300
          ${isDragging 
            ? 'border-primary bg-primary/10 scale-105' 
            : 'border-border glass-card hover:border-primary/50'
          }
        `}
      >
        <input
          type="file"
          accept={ACCEPTED_FORMATS.join(',')}
          onChange={handleFileInput}
          className="hidden"
          id="audio-upload"
        />
        
        {!selectedFile ? (
          <label
            htmlFor="audio-upload"
            className="flex flex-col items-center justify-center p-12 cursor-pointer"
          >
            <div className="w-20 h-20 rounded-full gradient-primary flex items-center justify-center mb-6 glow-primary">
              <Upload className="w-10 h-10 text-primary-foreground" />
            </div>
            
            <h3 className="text-2xl font-semibold mb-2 text-foreground">
              Drop your audio file here
            </h3>
            
            <p className="text-muted-foreground mb-6 text-center">
              or click to browse
            </p>
            
            <div className="flex flex-wrap gap-2 justify-center text-sm text-muted-foreground">
              <span className="px-3 py-1 rounded-full bg-muted">WAV</span>
              <span className="px-3 py-1 rounded-full bg-muted">MP3</span>
              <span className="px-3 py-1 rounded-full bg-muted">OGG</span>
              <span className="px-3 py-1 rounded-full bg-muted">WebM</span>
            </div>
            
            <div className="flex items-center gap-2 mt-6 text-xs text-muted-foreground">
              <AlertCircle className="w-4 h-4" />
              <span>Max 50MB • Up to 10 minutes</span>
            </div>
          </label>
        ) : (
          <div className="p-8">
            <div className="flex items-center justify-between p-4 rounded-xl bg-muted/50">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg gradient-primary flex items-center justify-center">
                  <FileAudio className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <p className="font-medium text-foreground">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              
              <button
                onClick={clearFile}
                className="p-2 rounded-lg hover:bg-muted transition-colors"
              >
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
