import { useState, useEffect } from 'react';
import { Mic, CheckCircle, Square } from 'lucide-react';
import clsx from 'clsx';

interface VoiceEnrollerProps {
    onEnrollComplete: () => void;
}

const VoiceEnroller = ({ onEnrollComplete }: VoiceEnrollerProps) => {
    const [isRecording, setIsRecording] = useState(false);
    const [progress, setProgress] = useState(0);
    const [isCompleted, setIsCompleted] = useState(false);

    useEffect(() => {
        let interval: number;
        if (isRecording) {
            interval = setInterval(() => {
                setProgress(prev => {
                    if (prev >= 100) {
                        setIsRecording(false);
                        setIsCompleted(true);
                        onEnrollComplete();
                        return 100;
                    }
                    return prev + 2; // 5 seconds to complete
                });
            }, 100);
        }
        return () => clearInterval(interval);
    }, [isRecording, onEnrollComplete]);

    return (
        <div className="flex flex-col items-center gap-4 p-6 bg-gray-50 rounded-2xl border border-gray-200">
            <h3 className="font-semibold text-gray-800">Voice Enrollment</h3>
            <p className="text-sm text-gray-500 text-center">
                Please read the following phrase aloud:
            </p>
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 w-full text-center font-medium text-gray-700 italic">
                "My name is [Your Name] and I confirm this order."
            </div>

            <div className="relative">
                <button
                    onClick={() => !isCompleted && setIsRecording(!isRecording)}
                    disabled={isCompleted}
                    className={clsx(
                        "w-16 h-16 rounded-full flex items-center justify-center transition-all shadow-lg",
                        isCompleted ? "bg-green-500 text-white" :
                            isRecording ? "bg-red-500 text-white animate-pulse" :
                                "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
                    )}
                >
                    {isCompleted ? <CheckCircle size={32} /> :
                        isRecording ? <Square size={24} /> :
                            <Mic size={32} />}
                </button>

                {isRecording && (
                    <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-xs font-medium text-gray-500 whitespace-nowrap">
                        Recording... {progress}%
                    </div>
                )}
            </div>

            {isCompleted && (
                <p className="text-sm text-green-600 font-medium">Voice enrolled successfully!</p>
            )}
        </div>
    );
};

export default VoiceEnroller;
