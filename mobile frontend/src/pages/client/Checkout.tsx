import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ShoppingBag, MapPin, CreditCard, ShieldCheck, Truck, X, Mic, CheckCircle } from 'lucide-react';
import { useDatabase } from '../../context/MockDatabaseContext';
import clsx from 'clsx';

const Checkout = () => {
    const navigate = useNavigate();
    const { updateOrder } = useDatabase();
    const [showVoiceModal, setShowVoiceModal] = useState(false);
    const [voiceStep, setVoiceStep] = useState(1);
    const [isRecording, setIsRecording] = useState(false);
    const [recordingProgress, setRecordingProgress] = useState(0);
    const [completedRecordings, setCompletedRecordings] = useState<number[]>([]);
    const [orderPlaced, setOrderPlaced] = useState(false);

    const handleStartRecording = () => {
        setIsRecording(true);
        setRecordingProgress(0);

        const interval = setInterval(() => {
            setRecordingProgress(prev => {
                if (prev >= 100) {
                    clearInterval(interval);
                    setIsRecording(false);
                    setCompletedRecordings(prev => [...prev, voiceStep]);

                    if (voiceStep < 3) {
                        setTimeout(() => setVoiceStep(voiceStep + 1), 500);
                    } else {
                        setTimeout(() => {
                            updateOrder('ORD-001', { voiceEnrolled: true });
                            setShowVoiceModal(false);
                            setOrderPlaced(true);
                        }, 1000);
                    }
                    return 100;
                }
                return prev + 3.33; // 3 seconds per recording
            });
        }, 100);
    };

    if (orderPlaced) {
        return (
            <div className="flex flex-col h-full bg-gray-50">
                <header className="bg-white p-4 shadow-sm flex items-center gap-3 border-b">
                    <button onClick={() => navigate(-1)} className="text-gray-600">
                        <ArrowLeft size={24} />
                    </button>
                    <h1 className="text-lg font-bold text-gray-800">Order Confirmation</h1>
                </header>

                <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                    <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center text-green-600 mb-6 animate-bounce">
                        <CheckCircle size={48} />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">Order Placed Successfully!</h2>
                    <p className="text-gray-600 mb-2">Order #ORD-001</p>
                    <p className="text-sm text-gray-500 mb-8 max-w-md">
                        Your voice has been securely enrolled. The courier will verify your identity via voice call before delivery.
                    </p>
                    <button
                        onClick={() => navigate('/client/dashboard')}
                        className="px-8 py-3 bg-blue-600 text-white rounded-lg font-bold shadow-lg hover:bg-blue-700 transition-colors"
                    >
                        View My Orders
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <header className="bg-white p-4 shadow-sm flex items-center gap-3 border-b">
                <button onClick={() => navigate(-1)} className="text-gray-600">
                    <ArrowLeft size={24} />
                </button>
                <h1 className="text-lg font-bold text-gray-800">Checkout</h1>
            </header>

            <div className="flex-1 overflow-y-auto p-4 pb-24">
                {/* Shipping Address */}
                <div className="bg-white rounded-lg shadow-sm mb-4 p-4 border">
                    <div className="flex items-center justify-between mb-3">
                        <h2 className="font-bold text-gray-800 flex items-center gap-2">
                            <MapPin size={18} className="text-blue-600" />
                            Shipping Address
                        </h2>
                        <button className="text-blue-600 text-sm font-medium">Change</button>
                    </div>
                    <div className="text-sm text-gray-700">
                        <p className="font-medium">John Doe</p>
                        <p>123, Galle Road</p>
                        <p>Colombo 03, Sri Lanka</p>
                        <p className="mt-1">+94 77 123 4567</p>
                    </div>
                </div>

                {/* Items */}
                <div className="bg-white rounded-lg shadow-sm mb-4 p-4 border">
                    <h2 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                        <ShoppingBag size={18} className="text-blue-600" />
                        Items (1)
                    </h2>
                    <div className="flex gap-3">
                        <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
                            <ShoppingBag size={32} className="text-gray-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="font-medium text-gray-800">Wireless Headphones</h3>
                            <p className="text-sm text-gray-500">Premium Noise Cancelling</p>
                            <p className="text-sm text-gray-600 mt-1">Qty: 1</p>
                        </div>
                        <div className="text-right">
                            <p className="font-bold text-gray-800">$120.00</p>
                        </div>
                    </div>
                </div>

                {/* Delivery */}
                <div className="bg-white rounded-lg shadow-sm mb-4 p-4 border">
                    <h2 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                        <Truck size={18} className="text-blue-600" />
                        Delivery Options
                    </h2>
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <div>
                            <p className="font-medium text-gray-800">Standard Delivery</p>
                            <p className="text-sm text-gray-600">Arrives in 2-3 business days</p>
                        </div>
                        <p className="font-bold text-gray-800">$5.00</p>
                    </div>
                </div>

                {/* Payment */}
                <div className="bg-white rounded-lg shadow-sm mb-4 p-4 border">
                    <h2 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                        <CreditCard size={18} className="text-blue-600" />
                        Payment Method
                    </h2>
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border">
                        <CreditCard size={24} className="text-gray-600" />
                        <div>
                            <p className="font-medium text-gray-800">Visa ending in 4242</p>
                            <p className="text-sm text-gray-600">Expires 12/25</p>
                        </div>
                    </div>
                </div>

                {/* Voice Security */}
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-sm mb-4 p-4 border border-blue-200">
                    <h2 className="font-bold text-gray-800 mb-2 flex items-center gap-2">
                        <ShieldCheck size={18} className="text-blue-600" />
                        Voice Security Enrollment
                    </h2>
                    <p className="text-sm text-gray-700 mb-3">
                        Protect your delivery with voice verification. The courier will verify your identity before handing over the package.
                    </p>
                    <div className="flex items-center gap-2 text-xs text-blue-700 bg-blue-100 p-2 rounded">
                        <ShieldCheck size={14} />
                        <span>Required for secure delivery</span>
                    </div>
                </div>
            </div>

            {/* Bottom Summary */}
            <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg p-4">
                <div className="space-y-2 mb-3">
                    <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Subtotal</span>
                        <span className="font-medium">$120.00</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Shipping</span>
                        <span className="font-medium">$5.00</span>
                    </div>
                    <div className="flex justify-between text-lg font-bold border-t pt-2">
                        <span>Total</span>
                        <span className="text-blue-600">$125.00</span>
                    </div>
                </div>
                <button
                    onClick={() => setShowVoiceModal(true)}
                    className="w-full py-3 bg-blue-600 text-white rounded-lg font-bold shadow-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                    <ShieldCheck size={20} />
                    Complete Order with Voice Security
                </button>
            </div>

            {/* Voice Enrollment Modal */}
            {showVoiceModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative">
                        <button
                            onClick={() => setShowVoiceModal(false)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
                        >
                            <X size={24} />
                        </button>

                        <div className="text-center mb-6">
                            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Mic size={32} className="text-blue-600" />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-800 mb-2">Voice Enrollment</h2>
                            <p className="text-sm text-gray-600">
                                Say your name 3 times to complete enrollment
                            </p>
                        </div>

                        {/* Progress Indicators */}
                        <div className="flex justify-center gap-3 mb-6">
                            {[1, 2, 3].map(step => (
                                <div
                                    key={step}
                                    className={clsx(
                                        "w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all",
                                        completedRecordings.includes(step)
                                            ? "bg-green-500 text-white"
                                            : voiceStep === step
                                                ? "bg-blue-600 text-white ring-4 ring-blue-200"
                                                : "bg-gray-200 text-gray-500"
                                    )}
                                >
                                    {completedRecordings.includes(step) ? <CheckCircle size={20} /> : step}
                                </div>
                            ))}
                        </div>

                        {/* Instructions */}
                        <div className="bg-blue-50 rounded-lg p-4 mb-6 border border-blue-200">
                            <p className="text-center font-medium text-gray-800 mb-2">
                                Recording {voiceStep} of 3
                            </p>
                            <p className="text-center text-lg font-bold text-blue-600 italic">
                                "My name is [Your Name]"
                            </p>
                        </div>

                        {/* Record Button */}
                        <div className="flex flex-col items-center">
                            <button
                                onClick={handleStartRecording}
                                disabled={isRecording || completedRecordings.includes(voiceStep)}
                                className={clsx(
                                    "w-20 h-20 rounded-full flex items-center justify-center transition-all shadow-lg mb-4",
                                    completedRecordings.includes(voiceStep)
                                        ? "bg-green-500 text-white"
                                        : isRecording
                                            ? "bg-red-500 text-white animate-pulse"
                                            : "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
                                )}
                            >
                                {completedRecordings.includes(voiceStep) ? (
                                    <CheckCircle size={40} />
                                ) : (
                                    <Mic size={40} />
                                )}
                            </button>

                            {isRecording && (
                                <div className="w-full">
                                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-blue-600 transition-all duration-100"
                                            style={{ width: `${recordingProgress}%` }}
                                        />
                                    </div>
                                    <p className="text-center text-sm text-gray-600 mt-2">
                                        Recording... {Math.round(recordingProgress)}%
                                    </p>
                                </div>
                            )}

                            {!isRecording && !completedRecordings.includes(voiceStep) && (
                                <p className="text-sm text-gray-600">Tap to start recording</p>
                            )}

                            {completedRecordings.includes(voiceStep) && voiceStep < 3 && (
                                <p className="text-sm text-green-600 font-medium">✓ Recording {voiceStep} complete</p>
                            )}

                            {completedRecordings.length === 3 && (
                                <p className="text-sm text-green-600 font-medium">✓ All recordings complete! Processing...</p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Checkout;
