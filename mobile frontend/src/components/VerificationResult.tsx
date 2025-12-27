import { CheckCircle, XCircle, Box } from 'lucide-react';
import clsx from 'clsx';
import { motion } from 'framer-motion';

interface VerificationResultProps {
    status: 'success' | 'failed' | 'locker';
    onReset: () => void;
}

const VerificationResult = ({ status, onReset }: VerificationResultProps) => {
    return (
        <div className="flex flex-col items-center justify-center p-6 text-center">
            <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className={clsx(
                    "w-24 h-24 rounded-full flex items-center justify-center mb-4",
                    status === 'success' ? "bg-green-100 text-green-600" :
                        status === 'failed' ? "bg-red-100 text-red-600" :
                            "bg-orange-100 text-orange-600"
                )}
            >
                {status === 'success' && <CheckCircle size={48} />}
                {status === 'failed' && <XCircle size={48} />}
                {status === 'locker' && <Box size={48} />}
            </motion.div>

            <h2 className="text-xl font-bold mb-2">
                {status === 'success' ? "Identity Verified!" :
                    status === 'failed' ? "Verification Failed" :
                        "Redirected to Smart Locker"}
            </h2>

            <p className="text-gray-600 mb-6">
                {status === 'success' ? "The neighbor's face matches the NIC provided. You may hand over the parcel." :
                    status === 'failed' ? "Face does not match the NIC. Please try again or use Smart Locker." :
                        "Due to verification failure, please deposit the parcel at the nearest Smart Locker."}
            </p>

            <div className="flex gap-3 w-full">
                <button
                    onClick={onReset}
                    className="flex-1 py-3 px-4 rounded-xl border border-gray-200 font-medium hover:bg-gray-50"
                >
                    Try Again
                </button>
                {status === 'failed' && (
                    <button
                        className="flex-1 py-3 px-4 rounded-xl bg-orange-600 text-white font-medium hover:bg-orange-700"
                    >
                        Use Locker
                    </button>
                )}
            </div>
        </div>
    );
};

export default VerificationResult;
