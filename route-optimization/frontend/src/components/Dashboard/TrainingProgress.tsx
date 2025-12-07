
import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { trainingAPI } from '../../services/api';
import { TrainingLog } from '../../types';

const TrainingProgress: React.FC = () => {
  const [logs, setLogs] = useState<TrainingLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrainingLogs();
  }, []);

  const fetchTrainingLogs = async () => {
    try {
      const response = await trainingAPI.getLatest();
      setLogs(response.data);
    } catch (error) {
      console.error('Failed to fetch training logs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
      </Paper>
    );
  }

  if (logs.length === 0) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="text.secondary" textAlign="center">
          No training logs available. Optimize a route to see training progress.
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Q-Learning Training Progress
      </Typography>
      
      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={logs}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="episode" 
              label={{ value: 'Episode', position: 'insideBottom', offset: -5 }} 
            />
            <YAxis 
              label={{ value: 'Average Distance (km)', angle: -90, position: 'insideLeft' }} 
            />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="average_distance" 
              stroke="#8884d8" 
              name="Avg Distance" 
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};