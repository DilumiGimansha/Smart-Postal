import { Camera } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface FaceScannerProps {
    onScanComplete: () => void;
    isScanning: boolean;
}

const FaceScanner = ({ onScanComplete, isScanning }: FaceScannerProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [hasPermission, setHasPermission] = useState(false);

    useEffect(() => {
        if (isScanning) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream;
                        setHasPermission(true);
                    }
                })
                .catch(err => {
                    console.error("Camera error:", err);
                    setHasPermission(false);
                });
        } else {
            // Stop stream
            if (videoRef.current?.srcObject) {
                const stream = videoRef.current.srcObject as MediaStream;
                stream.getTracks().forEach(track => track.stop());
            }
        }
    }, [isScanning]);

    return (
        <div className="relative w-full aspect-[3/4] bg-black rounded-2xl overflow-hidden shadow-lg">
            {isScanning ? (
                <>
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 border-4 border-blue-500/50 rounded-2xl pointer-events-none">
                        <div className="absolute top-1/4 left-1/4 right-1/4 bottom-1/4 border-2 border-white/80 rounded-full animate-pulse shadow-[0_0_100px_rgba(0,0,0,0.5)_inset]"></div>
                    </div>
                    <div className="absolute bottom-4 left-0 right-0 flex justify-center">
                        <button
                            onClick={onScanComplete}
                            className="bg-white text-blue-600 px-6 py-2 rounded-full font-bold shadow-lg active:scale-95 transition-transform flex items-center gap-2"
                        >
                            <Camera size={20} />
                            Capture & Verify
                        </button>
                    </div>
                </>
            ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-gray-400">
                    <Camera size={48} className="mb-2" />
                    <p>{hasPermission === false && isScanning ? "Camera access denied" : "Camera inactive"}</p>
                </div>
            )}
        </div>
    );
};

export default FaceScanner;
