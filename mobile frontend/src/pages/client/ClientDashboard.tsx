import { Package, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDatabase } from '../../context/MockDatabaseContext';

const ClientDashboard = () => {
    const { orders } = useDatabase();
    const navigate = useNavigate();

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <header className="bg-white p-4 shadow-sm">
                <h1 className="text-lg font-bold text-gray-800">My Parcels</h1>
                <p className="text-xs text-gray-500">Welcome back, Client</p>
            </header>

            <div className="p-4 flex flex-col gap-4">
                {orders.map(order => (
                    <div key={order.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                        <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-2">
                                <div className="bg-blue-50 p-2 rounded-lg text-blue-600">
                                    <Package size={20} />
                                </div>
                                <div>
                                    <h3 className="font-bold text-gray-800">{order.id}</h3>
                                    <p className="text-xs text-gray-500">{order.status.toUpperCase()}</p>
                                </div>
                            </div>
                        </div>

                        <p className="text-sm text-gray-600 mb-4">{order.address}</p>

                        {order.status === 'pending' && (
                            <button
                                onClick={() => navigate(`/client/authorize/${order.id}`)}
                                className="w-full py-2 px-4 bg-blue-50 text-blue-600 rounded-lg text-sm font-medium flex items-center justify-center gap-2 hover:bg-blue-100 transition-colors"
                            >
                                <ShieldCheck size={16} />
                                Authorize Neighbor
                            </button>
                        )}

                        {order.neighborNicImage && (
                            <div className="mt-2 text-xs text-green-600 flex items-center gap-1">
                                <ShieldCheck size={12} />
                                Neighbor Authorized
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ClientDashboard;
