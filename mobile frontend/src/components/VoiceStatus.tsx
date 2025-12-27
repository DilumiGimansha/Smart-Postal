import { ShieldCheck, ShieldAlert, Mic } from 'lucide-react';
import clsx from 'clsx';

interface VoiceStatusProps {
    status: 'listening' | 'human' | 'ai';
}

const VoiceStatus = ({ status }: VoiceStatusProps) => {
    return (
        <div className="flex flex-col items-center gap-4">
            <div className={clsx(
                "w-20 h-20 rounded-full flex items-center justify-center shadow-lg transition-colors duration-500",
                status === 'listening' ? "bg-blue-100 text-blue-600 animate-pulse" :
                    status === 'human' ? "bg-green-100 text-green-600" :
                        "bg-red-100 text-red-600"
            )}>
                {status === 'listening' && <Mic size={32} />}
                {status === 'human' && <ShieldCheck size={32} />}
                {status === 'ai' && <ShieldAlert size={32} />}
            </div>

            <div className="text-center">
                <h2 className="text-xl font-bold text-gray-800">
                    {status === 'listening' ? "Listening..." :
                        status === 'human' ? "Identity Verified" :
                            "AI Voice Detected!"}
                </h2>
                <p className={clsx("text-sm mt-1 font-medium",
                    status === 'ai' ? "text-red-500" : "text-gray-500"
                )}>
                    {status === 'listening' ? "Analyzing voice pattern..." :
                        status === 'human' ? "Caller is human and verified." :
                            "Potential fraud detected. Parcel on hold."}
                </p>
            </div>
        </div>
    );
};

export default VoiceStatus;
