import { useEffect, useRef } from 'react';

interface AudioVisualizerProps {
    isActive: boolean;
    isAiDetected: boolean;
}

const AudioVisualizer = ({ isActive, isAiDetected }: AudioVisualizerProps) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (!isActive) return;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationId: number;
        let time = 0;

        const draw = () => {
            time += 0.1;
            const width = canvas.width;
            const height = canvas.height;

            ctx.clearRect(0, 0, width, height);
            ctx.lineWidth = 2;
            ctx.strokeStyle = isAiDetected ? '#EF4444' : '#3B82F6'; // Red for AI, Blue for Human
            ctx.beginPath();

            for (let x = 0; x < width; x++) {
                // Create a waveform
                const y = height / 2 + Math.sin(x * 0.05 + time) * 20 * Math.sin(x * 0.01 + time * 0.5);
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }

            ctx.stroke();
            animationId = requestAnimationFrame(draw);
        };

        draw();

        return () => cancelAnimationFrame(animationId);
    }, [isActive, isAiDetected]);

    return (
        <div className="w-full h-32 bg-gray-900 rounded-xl overflow-hidden shadow-inner flex items-center justify-center">
            {isActive ? (
                <canvas ref={canvasRef} width={300} height={100} className="w-full h-full" />
            ) : (
                <div className="text-gray-600 text-sm">Waiting for voice...</div>
            )}
        </div>
    );
};

export default AudioVisualizer;
