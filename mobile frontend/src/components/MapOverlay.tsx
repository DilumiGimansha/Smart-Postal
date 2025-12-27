import { CloudRain, Navigation } from 'lucide-react';
import clsx from 'clsx';

interface MapOverlayProps {
    isRainMode: boolean;
    onToggleRainMode: () => void;
    deliveryCount: number;
}

const MapOverlay = ({ isRainMode, onToggleRainMode, deliveryCount }: MapOverlayProps) => {
    return (
        <div className="absolute bottom-20 left-4 right-4 z-[1000] flex flex-col gap-3">
            <div className="bg-white p-4 rounded-xl shadow-lg flex items-center justify-between">
                <div>
                    <h3 className="font-bold text-gray-800">Route Optimizer</h3>
                    <p className="text-xs text-gray-500">{deliveryCount} stops remaining</p>
                    {isRainMode && (
                        <p className="text-xs text-blue-600 font-bold mt-1 animate-pulse">
                            🚴 Bike Mode: Avoiding Rain
                        </p>
                    )}
                </div>
                <button
                    onClick={onToggleRainMode}
                    className={clsx(
                        "flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors",
                        isRainMode ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"
                    )}
                >
                    <CloudRain size={18} />
                    {isRainMode ? "Rain Mode ON" : "Rain Mode OFF"}
                </button>
            </div>

            <button className="bg-black text-white p-4 rounded-xl shadow-lg font-bold flex items-center justify-center gap-2 active:scale-95 transition-transform">
                <Navigation size={20} />
                Start Navigation
            </button>
        </div>
    );
};

export default MapOverlay;
