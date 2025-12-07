import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Stack,
  LinearProgress,
} from '@mui/material';
import { RouteRounded } from '@mui/icons-material';
import { routesAPI } from '../../services/api';

interface RouteOptimizerProps {
  selectedItems: number[];
  onOptimizationComplete: (result: any) => void;
}

const RouteOptimizer: React.FC<RouteOptimizerProps> = ({
  selectedItems,
  onOptimizationComplete,
}) => {
  const [routeName, setRouteName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    if (!routeName.trim()) {
      setError('Please enter a route name');
      return;
    }

    if (selectedItems.length === 0) {
      setError('Please select mail items to optimize');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await routesAPI.optimize(selectedItems, routeName);
      onOptimizationComplete(response.data);
      setRouteName(''); // Clear form
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to optimize route');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Route Optimization
      </Typography>

      <Stack spacing={2}>
        <Alert severity="info">
          Selected {selectedItems.length} mail item(s) for optimization
        </Alert>

        <TextField
          label="Route Name"
          value={routeName}
          onChange={(e) => setRouteName(e.target.value)}
          fullWidth
          placeholder="e.g., Route A - Colombo Central"
          disabled={loading}
        />

        {loading && (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Training Q-Learning model (1000 episodes)...
            </Typography>
            <LinearProgress />
          </Box>
        )}

        <Button
          variant="contained"
          size="large"
          startIcon={loading ? <CircularProgress size={20} /> : <RouteRounded />}
          onClick={handleOptimize}
          disabled={loading || selectedItems.length === 0}
          fullWidth
        >
          {loading ? 'Optimizing with Q-Learning...' : 'Optimize Route'}
        </Button>

        {error && <Alert severity="error">{error}</Alert>}
      </Stack>
    </Paper>
  );
};

export default RouteOptimizer;