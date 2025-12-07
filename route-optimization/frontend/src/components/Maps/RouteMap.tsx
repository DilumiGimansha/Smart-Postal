import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Chip,
  Alert,
} from '@mui/material';
import { GoogleMap, LoadScript, Polyline, Marker } from '@react-google-maps/api';
import { Timeline, TrendingUp } from '@mui/icons-material';

interface Coordinate {
  lat: number;
  lng: number;
  index: number;
}

interface RouteMapProps {
  optimizedRoute: Coordinate[];
  baselineRoute: Coordinate[];
  googleMapsApiKey: string;
}

const mapContainerStyle = {
  width: '100%',
  height: '500px',
};

const defaultCenter = {
  lat: 6.9271,
  lng: 79.8612,
};

const RouteMap: React.FC<RouteMapProps> = ({
  optimizedRoute,
  baselineRoute,
  googleMapsApiKey,
}) => {
  const [selectedRoute, setSelectedRoute] = useState<'optimized' | 'baseline' | 'both'>('optimized');
  const [loadError, setLoadError] = useState(false);

  const optimizedPath = optimizedRoute.map(coord => ({ lat: coord.lat, lng: coord.lng }));
  const baselinePath = baselineRoute.map(coord => ({ lat: coord.lat, lng: coord.lng }));

  const optimizedLineOptions = {
    strokeColor: '#4CAF50',
    strokeOpacity: 1,
    strokeWeight: 4,
    geodesic: true,
  };

  const baselineLineOptions = {
    strokeColor: '#FF5252',
    strokeOpacity: 0.7,
    strokeWeight: 3,
    geodesic: true,
  };

  if (!googleMapsApiKey) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="warning">
          Google Maps API key not configured. Click the settings icon (⚙️) to add your API key.
        </Alert>
      </Paper>
    );
  }

  if (loadError) {
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load Google Maps. Please check your API key and internet connection.
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Route Visualization</Typography>
        <ToggleButtonGroup
          value={selectedRoute}
          exclusive
          onChange={(_, newValue) => newValue && setSelectedRoute(newValue)}
          size="small"
        >
          <ToggleButton value="optimized">
            <TrendingUp sx={{ mr: 0.5 }} /> Optimized
          </ToggleButton>
          <ToggleButton value="baseline">
            <Timeline sx={{ mr: 0.5 }} /> Baseline
          </ToggleButton>
          <ToggleButton value="both">Both</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Box mb={2} display="flex" gap={2} flexWrap="wrap">
        <Chip
          label="Optimized Route (Green)"
          sx={{ bgcolor: '#4CAF50', color: 'white' }}
          size="small"
        />
        <Chip
          label="Baseline Route (Red)"
          sx={{ bgcolor: '#FF5252', color: 'white' }}
          size="small"
        />
        <Chip
          label="🏢 Depot"
          variant="outlined"
          size="small"
        />
      </Box>

      <LoadScript 
        googleMapsApiKey={googleMapsApiKey}
        onError={() => setLoadError(true)}
      >
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={defaultCenter}
          zoom={12}
          options={{
            zoomControl: true,
            streetViewControl: false,
            mapTypeControl: true,
            fullscreenControl: true,
          }}
        >
          {/* Optimized Route */}
          {(selectedRoute === 'optimized' || selectedRoute === 'both') && (
            <>
              <Polyline path={optimizedPath} options={optimizedLineOptions} />
              {optimizedRoute.map((coord, idx) => (
                <Marker
                  key={`opt-${idx}`}
                  position={{ lat: coord.lat, lng: coord.lng }}
                  label={{
                    text: coord.index === 0 ? '🏢' : `${coord.index}`,
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: 'bold',
                  }}
                  icon={
                    coord.index === 0
                      ? undefined
                      : {
                          path: 0, // Circle
                          scale: 8,
                          fillColor: '#4CAF50',
                          fillOpacity: 1,
                          strokeColor: 'white',
                          strokeWeight: 2,
                        }
                  }
                />
              ))}
            </>
          )}

          {/* Baseline Route */}
          {(selectedRoute === 'baseline' || selectedRoute === 'both') && (
            <>
              <Polyline path={baselinePath} options={baselineLineOptions} />
              {selectedRoute === 'baseline' &&
                baselineRoute.map((coord, idx) => (
                  <Marker
                    key={`base-${idx}`}
                    position={{ lat: coord.lat, lng: coord.lng }}
                    label={{
                      text: coord.index === 0 ? '🏢' : `${coord.index}`,
                      color: 'white',
                      fontSize: '12px',
                      fontWeight: 'bold',
                    }}
                    icon={
                      coord.index === 0
                        ? undefined
                        : {
                            path: 0,
                            scale: 8,
                            fillColor: '#FF5252',
                            fillOpacity: 1,
                            strokeColor: 'white',
                            strokeWeight: 2,
                          }
                    }
                  />
                ))}
            </>
          )}
        </GoogleMap>
      </LoadScript>
    </Paper>
  );
};

export default RouteMap;