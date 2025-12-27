import { Package, MapPin, Truck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDatabase } from '../../context/MockDatabaseContext';

const CourierDashboard = () => {
    const { orders } = useDatabase();
    const navigate = useNavigate();

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <header className="bg-white p-4 shadow-sm">
                <h1 className="text-lg font-bold text-gray-800">Delivery List</h1>
                <p className="text-xs text-gray-500">Today's Route</p>
                <button
                    onClick={() => navigate('/route')}
                    className="mt-2 w-full py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium flex items-center justify-center gap-2"
                >
                    <MapPin size={16} /> View Optimized Route
                </button>
            </header>

            <div className="p-4 flex flex-col gap-4">
                {orders.map(order => (
                    <div key={order.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                        <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center gap-2">
                                <div className="bg-green-50 p-2 rounded-lg text-green-600">
                                    <Package size={20} />
                                </div>
                                <div>
                                    <h3 className="font-bold text-gray-800">{order.id}</h3>
                                    <p className="text-xs text-gray-500">{order.recipientName}</p>
                                </div>
                            </div>
                            <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium text-gray-600">
                                {order.status.toUpperCase()}
                            </span>
                        </div>

                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                            <MapPin size={16} />
                            {order.address}
                        </div>

                        <button
                            onClick={() => navigate(`/courier/delivery/${order.id}`)}
                            className="w-full py-2 px-4 bg-green-600 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2 hover:bg-green-700 transition-colors shadow-sm"
                        >
                            <Truck size={16} />
                            Start Delivery
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CourierDashboard;
