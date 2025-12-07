import React from 'react';
import {
  Paper,
  Typography,
  Grid,
  Box,
  Chip,
} from '@mui/material';
import {
  TrendingDown,
  Speed,
  LocalGasStation,
} from '@mui/icons-material';

interface RouteComparisonProps {
  optimizedMetrics: {
    total_distance: number;
    estimated_time: number;
  };
  baselineMetrics: {
    total_distance: number;
    estimated_time: number;
  };
  improvement: {
    distance_saved_km: number;
    fuel_saving_percentage: number;
    time_saved_minutes: number;
  };
}

const RouteComparison: React.FC<RouteComparisonProps> = ({
  optimizedMetrics,
  baselineMetrics,
  improvement,
}) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Route Performance Comparison
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Box sx={{ textAlign: 'center' }}>
            <TrendingDown sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" color="success.main">
              {improvement.distance_saved_km.toFixed(2)} km
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Distance Saved
            </Typography>
            <Chip
              label={`${improvement.fuel_saving_percentage.toFixed(1)}% fuel saved`}
              color="success"
              size="small"
              sx={{ mt: 1 }}
            />
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <Box sx={{ textAlign: 'center' }}>
            <Speed sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" color="primary.main">
              {improvement.time_saved_minutes} min
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Time Saved
            </Typography>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <Box sx={{ textAlign: 'center' }}>
            <LocalGasStation sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" color="info.main">
              {optimizedMetrics.total_distance.toFixed(2)} km
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Optimized Distance
            </Typography>
            <Typography variant="caption" color="text.secondary">
              (vs {baselineMetrics.total_distance.toFixed(2)} km baseline)
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default RouteComparison;