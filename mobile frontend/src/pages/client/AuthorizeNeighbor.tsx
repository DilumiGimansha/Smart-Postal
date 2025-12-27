import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import NicUploader from '../../components/NicUploader';
import { useDatabase } from '../../context/MockDatabaseContext';

const AuthorizeNeighbor = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { updateOrder } = useDatabase();
    const [neighborName, setNeighborName] = useState('');

    const handleImageSelected = (url: string) => {
        if (id) {
            updateOrder(id, {
                neighborNicImage: url,
                neighborName: neighborName || 'Neighbor'
            });
            // Go back after short delay
            setTimeout(() => navigate('/client/dashboard'), 1500);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <header className="bg-white p-4 shadow-sm flex items-center gap-3">
                <button onClick={() => navigate(-1)} className="text-gray-600">
                    <ArrowLeft size={24} />
                </button>
                <div>
                    <h1 className="text-lg font-bold text-gray-800">Authorize Neighbor</h1>
                    <p className="text-xs text-gray-500">Order #{id}</p>
                </div>
            </header>

            <div className="p-4 flex flex-col gap-6">
                <div className="bg-white p-4 rounded-2xl shadow-sm">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Neighbor's Name (Optional)</label>
                    <input
                        type="text"
                        value={neighborName}
                        onChange={(e) => setNeighborName(e.target.value)}
                        placeholder="Enter name"
                        className="w-full p-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 mb-4"
                    />

                    <label className="block text-sm font-medium text-gray-700 mb-2">Upload Neighbor's NIC</label>
                    <NicUploader onImageSelected={handleImageSelected} />
                </div>

                <p className="text-xs text-gray-500 text-center px-4">
                    By uploading this image, you authorize the courier to hand over the parcel to the person matching this ID.
                </p>
            </div>
        </div>
    );
};

export default AuthorizeNeighbor;
