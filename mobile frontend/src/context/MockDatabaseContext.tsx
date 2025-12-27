import { createContext, useContext, useState, type ReactNode } from 'react';

export interface DeliveryOrder {
    id: string;
    recipientName: string;
    address: string;
    status: 'pending' | 'delivered' | 'locker';
    neighborNicImage?: string; // URL of uploaded NIC
    neighborName?: string;
    voiceEnrolled?: boolean;
    lat?: number;
    lng?: number;
}

interface DatabaseContextType {
    orders: DeliveryOrder[];
    updateOrder: (id: string, updates: Partial<DeliveryOrder>) => void;
    currentUserRole: 'client' | 'courier' | null;
    setRole: (role: 'client' | 'courier' | null) => void;
    isAuthenticated: boolean;
    currentUser: string | null;
    login: (username: string, password: string) => boolean;
    logout: () => void;
}

const DatabaseContext = createContext<DatabaseContextType | undefined>(undefined);

export const DatabaseProvider = ({ children }: { children: ReactNode }) => {
    const [currentUserRole, setRole] = useState<'client' | 'courier' | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [currentUser, setCurrentUser] = useState<string | null>(null);

    // Mock initial data
    const [orders, setOrders] = useState<DeliveryOrder[]>([
        {
            id: 'ORD-001',
            recipientName: 'Kamal Perera',
            address: '123, Galle Road, Colombo 03',
            status: 'pending',
            voiceEnrolled: false,
            lat: 6.9271,
            lng: 79.8612
        },
        {
            id: 'ORD-002',
            recipientName: 'Nimali Silva',
            address: '45/B, Kandy Road, Kelaniya',
            status: 'pending',
            voiceEnrolled: true,
            lat: 6.9147,
            lng: 79.8778
        },
        {
            id: 'ORD-003',
            recipientName: 'Sunil Perera',
            address: '10, Duplication Road, Colombo 04',
            status: 'pending',
            voiceEnrolled: false,
            lat: 6.8969,
            lng: 79.8587
        }
    ]);

    const updateOrder = (id: string, updates: Partial<DeliveryOrder>) => {
        setOrders(prev => prev.map(order =>
            order.id === id ? { ...order, ...updates } : order
        ));
    };

    const login = (username: string, password: string): boolean => {
        // Mock authentication
        if (username === 'client' && password === 'client123') {
            setIsAuthenticated(true);
            setCurrentUser('client');
            setRole('client');
            return true;
        } else if (username === 'courier' && password === 'courier123') {
            setIsAuthenticated(true);
            setCurrentUser('courier');
            setRole('courier');
            return true;
        }
        return false;
    };

    const logout = () => {
        setIsAuthenticated(false);
        setCurrentUser(null);
        setRole(null);
    };

    return (
        <DatabaseContext.Provider value={{ orders, updateOrder, currentUserRole, setRole, isAuthenticated, currentUser, login, logout }}>
            {children}
        </DatabaseContext.Provider>
    );
};

export const useDatabase = () => {
    const context = useContext(DatabaseContext);
    if (!context) {
        throw new Error('useDatabase must be used within a DatabaseProvider');
    }
    return context;
};
