import { Upload } from 'lucide-react';
import { useRef, useState } from 'react';

interface NicUploaderProps {
    onImageSelected: (imageUrl: string) => void;
}

const NicUploader = ({ onImageSelected }: NicUploaderProps) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [preview, setPreview] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const url = URL.createObjectURL(file);
            setPreview(url);
            onImageSelected(url);
        }
    };

    return (
        <div className="w-full">
            <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center justify-center bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors h-48"
            >
                {preview ? (
                    <img src={preview} alt="NIC Preview" className="h-full object-contain rounded-lg" />
                ) : (
                    <>
                        <div className="bg-blue-100 p-3 rounded-full mb-3 text-blue-600">
                            <Upload size={24} />
                        </div>
                        <p className="text-sm font-medium text-gray-700">Upload Neighbor's NIC</p>
                        <p className="text-xs text-gray-500 mt-1">Supports old/faded IDs</p>
                    </>
                )}
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    accept="image/*"
                    className="hidden"
                />
            </div>
        </div>
    );
};

export default NicUploader;
