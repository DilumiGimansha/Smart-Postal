import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { NORMAL_ROUTE, RAIN_SAFE_ROUTE, RAIN_ZONES } from '../lib/mockRoutes';
import MapOverlay from '../components/MapOverlay';
import { useDatabase } from '../context/MockDatabaseContext';
import L from 'leaflet';

// Fix Leaflet icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const RouteMap = () => {
    const [isRainMode, setIsRainMode] = useState(false);
    const { orders } = useDatabase();

    return (
        <div className="relative h-full w-full">
            {/* @ts-ignore */}
            <MapContainer
                center={[6.9000, 79.8700]}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
                zoomControl={false}
            >
                {/* @ts-ignore */}
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {orders.filter(o => o.lat && o.lng).map(order => (
                    <Marker key={order.id} position={[order.lat!, order.lng!]}>
                        <Popup>
                            <div className="p-2">
                                <h3 className="font-bold text-blue-600 text-base mb-1">📦 {order.id}</h3>
                                <p className="text-sm font-medium text-gray-800">{order.recipientName}</p>
                                <p className="text-xs text-gray-500">{order.address}</p>
                            </div>
                        </Popup>
                    </Marker>
                ))}

                {/* @ts-ignore */}
                <Polyline
                    positions={isRainMode ? RAIN_SAFE_ROUTE : NORMAL_ROUTE}
                    color={isRainMode ? '#3B82F6' : '#EF4444'}
                    weight={4}
                    dashArray={isRainMode ? '10, 10' : undefined}
                />

                {/* @ts-ignore */}
                {isRainMode && RAIN_ZONES.map(zone => (
                    /* @ts-ignore */
                    <Circle
                        key={zone.id}
                        center={[zone.lat, zone.lng]}
                        radius={zone.radius}
                        pathOptions={{
                            color: '#3B82F6',
                            fillColor: '#3B82F6',
                            fillOpacity: 0.4,
                            weight: 1
                        }}
                    />
                ))}
            </MapContainer>

            <MapOverlay
                isRainMode={isRainMode}
                onToggleRainMode={() => setIsRainMode(!isRainMode)}
                deliveryCount={orders.length}
            />
        </div>
    );
};

export default RouteMap;
