import { useState } from 'react';
import NicUploader from '../components/NicUploader';
import FaceScanner from '../components/FaceScanner';
import VerificationResult from '../components/VerificationResult';

const DeliveryHandover = () => {
    const [step, setStep] = useState<'upload' | 'scan' | 'result'>('upload');
    const [nicImage, setNicImage] = useState<string | null>(null);
    const [resultStatus, setResultStatus] = useState<'success' | 'failed' | 'locker'>('success');

    const handleImageSelected = (url: string) => {
        setNicImage(url);
        // Simulate processing delay then move to scan
        setTimeout(() => setStep('scan'), 1000);
    };

    const handleScanComplete = () => {
        // Mock verification logic
        // Randomly succeed or fail for demo purposes, or succeed if we want a happy path
        const isSuccess = Math.random() > 0.3;
        setResultStatus(isSuccess ? 'success' : 'failed');
        setStep('result');
    };

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <header className="bg-white p-4 shadow-sm">
                <h1 className="text-lg font-bold text-gray-800">Secure Handover</h1>
                <p className="text-xs text-gray-500">Identity Verification</p>
            </header>

            <div className="flex-1 p-4 overflow-y-auto">
                {step === 'upload' && (
                    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="bg-white p-4 rounded-2xl shadow-sm">
                            <h2 className="font-semibold mb-2">Step 1: Neighbor Authorization</h2>
                            <p className="text-sm text-gray-600 mb-4">Upload the neighbor's NIC image provided by the recipient.</p>
                            <NicUploader onImageSelected={handleImageSelected} />
                        </div>
                    </div>
                )}

                {step === 'scan' && (
                    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="bg-white p-4 rounded-2xl shadow-sm">
                            <h2 className="font-semibold mb-2">Step 2: Face Verification</h2>
                            <p className="text-sm text-gray-600 mb-4">Scan the neighbor's face to verify against the NIC.</p>
                            <FaceScanner isScanning={true} onScanComplete={handleScanComplete} />
                        </div>
                        {nicImage && (
                            <div className="bg-white p-3 rounded-xl shadow-sm flex items-center gap-3 opacity-70">
                                <img src={nicImage} alt="NIC" className="w-12 h-8 object-cover rounded" />
                                <span className="text-sm text-gray-500">Matching against uploaded NIC...</span>
                            </div>
                        )}
                    </div>
                )}

                {step === 'result' && (
                    <div className="bg-white rounded-2xl shadow-sm animate-in zoom-in duration-300">
                        <VerificationResult
                            status={resultStatus}
                            onReset={() => setStep('upload')}
                        />
                    </div>
                )}
            </div>
        </div>
    );
};

export default DeliveryHandover;
