import { useState } from 'react';
import { AudioUploader } from '@/components/AudioUploader';
import { ProcessingStatus } from '@/components/ProcessingStatus';
import { AudioPlayer } from '@/components/AudioPlayer';
import { Sparkles, Wand2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import logo from '@/assets/logo.png';

const Index = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processingStatus, setProcessingStatus] = useState<'idle' | 'processing' | 'completed' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [processedAudioUrl, setProcessedAudioUrl] = useState<string | null>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setProcessingStatus('idle');
    setProcessedAudioUrl(null);
  };

  const handleProcess = () => {
    if (!selectedFile) return;

    setProcessingStatus('processing');
    setProgress(0);

    // Simulate processing (will be replaced with actual backend call)
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setProcessingStatus('completed');
          // For demo: use the original file as processed
          setProcessedAudioUrl(URL.createObjectURL(selectedFile));
          return 100;
        }
        return prev + 5;
      });
    }, 200);
  };

  const handleDownload = () => {
    if (!processedAudioUrl) return;
    
    const a = document.createElement('a');
    a.href = processedAudioUrl;
    a.download = `denoised_${selectedFile?.name || 'audio.wav'}`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary/20 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-border/50 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 flex items-center justify-center">
                <img src={logo} alt="AI Audio Isolator Logo" className="w-10 h-10 object-contain" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">AI Audio Isolator</h1>
                <p className="text-sm text-muted-foreground">Professional noise isolation system by Team Rafael</p>
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="container mx-auto px-4 py-12">
          {/* Hero section */}
          {!selectedFile && processingStatus === 'idle' && (
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-6">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-sm text-muted-foreground">Powered by Spectrogram based U-Net</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
                Clean Your Audio in Seconds
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Remove background noise, enhance clarity, and restore professional quality to your audio files using our trained ML model
              </p>
            </div>
          )}

          {/* Upload section */}
          <AudioUploader onFileSelect={handleFileSelect} />

          {/* Process button */}
          {selectedFile && processingStatus === 'idle' && (
            <div className="flex justify-center mt-8">
              <Button
                onClick={handleProcess}
                size="lg"
                className="gradient-primary glow-primary gap-2 text-lg px-8 py-6"
              >
                <Wand2 className="w-5 h-5" />
                Start Isolating Audio
              </Button>
            </div>
          )}

          {/* Processing status */}
          <ProcessingStatus
            status={processingStatus}
            progress={progress}
            message={
              processingStatus === 'processing' 
                ? 'Analyzing and removing noise patterns...'
                : processingStatus === 'completed'
                ? 'Your audio has been successfully enhanced!'
                : undefined
            }
          />

          {/* Audio player */}
          {processingStatus === 'completed' && processedAudioUrl && (
            <AudioPlayer
              audioUrl={processedAudioUrl}
              title="Enhanced Audio"
              onDownload={handleDownload}
            />
          )}

          {/* Features section */}
          {!selectedFile && processingStatus === 'idle' && (
            <div className="mt-20 grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              {[
                {
                  title: 'U-Net Powered',
                  description: 'Convolution neural networks trained on hundreds of audio samples'
                },
                {
                  title: 'Fast Processing',
                  description: 'Get your cleaned audio in seconds, not minutes'
                },
                {
                  title: 'Multi Linguistic',
                  description: 'The ML model has been trained in various languages'
                }
              ].map((feature, i) => (
                <div key={i} className="glass-card rounded-xl p-6 text-center">
                  <h3 className="text-lg font-semibold text-foreground mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Index;
