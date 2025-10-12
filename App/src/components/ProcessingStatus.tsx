import { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface ProcessingStatusProps {
  status: 'idle' | 'processing' | 'completed' | 'error';
  progress: number;
  message?: string;
}

export const ProcessingStatus = ({ status, progress, message }: ProcessingStatusProps) => {
  const [displayProgress, setDisplayProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setDisplayProgress((prev) => {
        if (prev >= progress) {
          clearInterval(timer);
          return progress;
        }
        return prev + 1;
      });
    }, 20);

    return () => clearInterval(timer);
  }, [progress]);

  if (status === 'idle') return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-8">
      <div className="glass-card rounded-2xl p-8">
        <div className="flex items-center gap-4 mb-6">
          {status === 'processing' && (
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          )}
          {status === 'completed' && (
            <CheckCircle2 className="w-8 h-8 text-green-500" />
          )}
          {status === 'error' && (
            <AlertCircle className="w-8 h-8 text-destructive" />
          )}
          
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-foreground">
              {status === 'processing' && 'Processing your audio...'}
              {status === 'completed' && 'Processing complete!'}
              {status === 'error' && 'Processing failed'}
            </h3>
            {message && (
              <p className="text-sm text-muted-foreground mt-1">{message}</p>
            )}
          </div>
        </div>

        {status === 'processing' && (
          <div className="space-y-3">
            <Progress value={displayProgress} className="h-2" />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Noise isolation in progress</span>
              <span>{displayProgress}%</span>
            </div>
          </div>
        )}

        {status === 'processing' && (
          <div className="mt-6 space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-muted-foreground">Analyzing audio patterns</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 rounded-full bg-secondary animate-pulse delay-100" />
              <span className="text-muted-foreground">Updating weights and biases</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 rounded-full bg-accent animate-pulse delay-200" />
              <span className="text-muted-foreground">Optimizing output quality</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
