import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import AiSupport from './pages/AiSupport';
import CourierCall from './pages/CourierCall';
import RouteMap from './pages/RouteMap';
import ClientDashboard from './pages/client/ClientDashboard';
import AuthorizeNeighbor from './pages/client/AuthorizeNeighbor';
import Checkout from './pages/client/Checkout';
import CourierDashboard from './pages/courier/CourierDashboard';
import DeliveryDetail from './pages/courier/DeliveryDetail';
import { DatabaseProvider, useDatabase } from './context/MockDatabaseContext';

const RoleBasedRedirect = () => {
  const { currentUserRole } = useDatabase();

  if (currentUserRole === 'client') {
    return <Navigate to="/client/dashboard" replace />;
  } else if (currentUserRole === 'courier') {
    return <Navigate to="/courier/dashboard" replace />;
  }

  return <Navigate to="/login" replace />;
};

function App() {
  return (
    <DatabaseProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/client/checkout" element={<Checkout />} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<RoleBasedRedirect />} />

            {/* Client Routes */}
            <Route path="client/dashboard" element={<ClientDashboard />} />
            <Route path="client/authorize/:id" element={<AuthorizeNeighbor />} />

            {/* Courier Routes */}
            <Route path="courier/dashboard" element={<CourierDashboard />} />
            <Route path="courier/delivery/:id" element={<DeliveryDetail />} />

            {/* Other Functions */}
            <Route path="ai-support" element={<AiSupport />} />
            <Route path="call" element={<CourierCall />} />
            <Route path="route" element={<RouteMap />} />
          </Route>
        </Routes>
      </Router>
    </DatabaseProvider>
  );
}

export default App;
