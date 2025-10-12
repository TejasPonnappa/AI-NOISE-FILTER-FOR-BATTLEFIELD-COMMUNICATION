import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Download, Volume2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';

interface AudioPlayerProps {
  audioUrl: string;
  title: string;
  onDownload?: () => void;
}

export const AudioPlayer = ({ audioUrl, title, onDownload }: AudioPlayerProps) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(80);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, []);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume / 100;
    }
  }, [volume]);

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (value: number[]) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = value[0];
    setCurrentTime(value[0]);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-8">
      <div className="glass-card rounded-2xl p-8">
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-foreground mb-2">{title}</h3>
          <p className="text-sm text-muted-foreground">
            AI-Enhanced Audio • Ready to download
          </p>
        </div>

        {/* Waveform visualization placeholder */}
        <div className="h-24 mb-6 rounded-lg bg-muted/30 flex items-center justify-center overflow-hidden">
          <div className="flex items-end gap-1 h-full p-4">
            {Array.from({ length: 60 }).map((_, i) => (
              <div
                key={i}
                className="flex-1 bg-gradient-to-t from-primary to-secondary rounded-full transition-all duration-300"
                style={{
                  height: `${Math.random() * 100}%`,
                  opacity: currentTime > (duration * i) / 60 ? 1 : 0.3
                }}
              />
            ))}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-6">
          <Slider
            value={[currentTime]}
            max={duration || 100}
            step={0.1}
            onValueChange={handleSeek}
            className="mb-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-4">
          <Button
            onClick={togglePlay}
            size="lg"
            className="rounded-full w-14 h-14 gradient-primary glow-primary"
          >
            {isPlaying ? (
              <Pause className="w-6 h-6" />
            ) : (
              <Play className="w-6 h-6 ml-1" />
            )}
          </Button>

          <div className="flex items-center gap-2 flex-1">
            <Volume2 className="w-5 h-5 text-muted-foreground" />
            <Slider
              value={[volume]}
              max={100}
              step={1}
              onValueChange={(value) => setVolume(value[0])}
              className="w-24"
            />
          </div>

          {onDownload && (
            <Button
              onClick={onDownload}
              variant="outline"
              className="gap-2"
            >
              <Download className="w-4 h-4" />
              Download
            </Button>
          )}
        </div>

        <audio ref={audioRef} src={audioUrl} preload="metadata" />
      </div>
    </div>
  );
};
