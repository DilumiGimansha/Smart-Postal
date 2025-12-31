import AdminLayout from '../../components/admin/AdminLayout';
import DataTable from '../../components/admin/DataTable';
import { Blocks, Activity, CheckCircle, AlertCircle } from 'lucide-react';

interface Transaction {
  hash: string;
  type: string;
  parcelId: string;
  timestamp: string;
  status: 'confirmed' | 'pending' | 'failed';
}

const BlockchainMonitor = () => {
  const mockTransactions: Transaction[] = [
    {
      hash: '0x1a2b3c...',
      type: 'Delivery Confirmation',
      parcelId: 'SP-12345',
      timestamp: '2024-12-30 12:45:23',
      status: 'confirmed',
    },
    {
      hash: '0x4d5e6f...',
      type: 'Identity Verification',
      parcelId: 'U-001',
      timestamp: '2024-12-30 12:40:15',
      status: 'confirmed',
    },
    {
      hash: '0x7g8h9i...',
      type: 'Payment Release',
      parcelId: 'SP-12346',
      timestamp: '2024-12-30 12:35:42',
      status: 'pending',
    },
    {
      hash: '0xjklmno...',
      type: 'Parcel Registration',
      parcelId: 'SP-12347',
      timestamp: '2024-12-30 12:30:18',
      status: 'confirmed',
    },
  ];

  const columns = [
    {
      header: 'Transaction Hash',
      accessor: 'hash' as keyof Transaction,
      className: 'font-mono text-xs',
    },
    {
      header: 'Type',
      accessor: 'type' as keyof Transaction,
      className: 'font-medium',
    },
    {
      header: 'Reference ID',
      accessor: 'parcelId' as keyof Transaction,
      className: 'font-mono',
    },
    {
      header: 'Timestamp',
      accessor: 'timestamp' as keyof Transaction,
    },
    {
      header: 'Status',
      accessor: ((row: Transaction) => (
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${
            row.status === 'confirmed'
              ? 'bg-green-100 text-green-700'
              : row.status === 'pending'
              ? 'bg-yellow-100 text-yellow-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {row.status.toUpperCase()}
        </span>
      )) as any,
    },
  ];

  const handleRowClick = (tx: Transaction) => {
    console.log('Transaction clicked:', tx);
    // TODO: Show transaction details
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Blockchain Monitor</h1>
          <p className="text-gray-600 mt-2">Monitor blockchain transactions and smart contracts</p>
        </div>

        {/* Network Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center gap-2">
              <Blocks className="w-5 h-5 text-indigo-600" />
              <p className="text-sm text-gray-600">Network Status</p>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <p className="text-lg font-bold text-gray-900">Active</p>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              <p className="text-sm text-gray-600">Block Height</p>
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-1">1,234,567</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <p className="text-sm text-gray-600">Confirmed Tx</p>
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-1">8,472</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <p className="text-sm text-gray-600">Pending Tx</p>
            </div>
            <p className="text-2xl font-bold text-gray-900 mt-1">23</p>
          </div>
        </div>

        {/* Smart Contracts */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Deployed Smart Contracts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { name: 'Parcel Tracking', address: '0xABCD...1234', status: 'Active' },
              { name: 'Identity Verification', address: '0xEFGH...5678', status: 'Active' },
              { name: 'Payment Escrow', address: '0xIJKL...9012', status: 'Active' },
              { name: 'Dispute Resolution', address: '0xMNOP...3456', status: 'Active' },
            ].map((contract) => (
              <div
                key={contract.name}
                className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{contract.name}</h3>
                    <p className="text-sm text-gray-500 font-mono mt-1">{contract.address}</p>
                  </div>
                  <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                    {contract.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Recent Transactions</h2>
          <DataTable data={mockTransactions} columns={columns} onRowClick={handleRowClick} />
        </div>

        {/* Gas Fees */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Gas Fee Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Average Gas Price</p>
              <p className="text-2xl font-bold text-gray-900">25 Gwei</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Total Gas Used (24h)</p>
              <p className="text-2xl font-bold text-gray-900">0.45 ETH</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Avg. Transaction Cost</p>
              <p className="text-2xl font-bold text-gray-900">$2.34</p>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

export default BlockchainMonitor;
