import { useState } from 'react';
import {
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
} from '@mui/material';
import { LocalShipping, Settings } from '@mui/icons-material';
import CSVUpload from './components/RouteOptimization/CSVUpload';
import ManualEntryForm from './components/RouteOptimization/ManualEntryForm';
import MailItemsList from './components/RouteOptimization/MailItemsList';
import RouteOptimizer from './components/RouteOptimization/RouteOptimizer';
import TrainingProgress from './components/Dashboard/TrainingProgress';
import RouteComparison from './components/Dashboard/RouteComparison';
import RouteMap from './components/Maps/RouteMap';
import { OptimizationResult } from './types';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [refreshList, setRefreshList] = useState(false);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  
  // Google Maps API Key Dialog
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState(false);
  const [googleMapsApiKey, setGoogleMapsApiKey] = useState(
    localStorage.getItem('googleMapsApiKey') || ''
  );

  const handleUploadSuccess = () => {
    setRefreshList(!refreshList);
  };

  const handleOptimizationComplete = (result: OptimizationResult) => {
    setOptimizationResult(result);
    setCurrentTab(1); // Switch to dashboard
  };

  const handleSaveApiKey = () => {
    localStorage.setItem('googleMapsApiKey', googleMapsApiKey);
    setApiKeyDialogOpen(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <AppBar position="static">
          <Toolbar>
            <LocalShipping sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Smart Postal System - Route Optimization
            </Typography>
            <IconButton
              color="inherit"
              onClick={() => setApiKeyDialogOpen(true)}
              title="Configure Google Maps API Key"
            >
              <Settings />
            </IconButton>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
          {!googleMapsApiKey && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Google Maps API key not configured. Click the settings icon ⚙️ to add your API key for map visualization.
            </Alert>
          )}

          <Tabs
            value={currentTab}
            onChange={(_, newValue) => setCurrentTab(newValue)}
            sx={{ mb: 3 }}
          >
            <Tab label="Route Optimization" />
            <Tab label="Dashboard & Maps" />
          </Tabs>

          {currentTab === 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <CSVUpload onUploadSuccess={handleUploadSuccess} />
              <ManualEntryForm onSuccess={handleUploadSuccess} />
              <MailItemsList
                refresh={refreshList}
                onSelectionChange={setSelectedItems}
              />
              <RouteOptimizer
                selectedItems={selectedItems}
                onOptimizationComplete={handleOptimizationComplete}
              />
            </Box>
          )}

          {currentTab === 1 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {!optimizationResult && (
                <Alert severity="info">
                  No route optimization results yet. Please optimize a route first from the "Route Optimization" tab.
                </Alert>
              )}
              
              <TrainingProgress />
              
              {optimizationResult && (
                <>
                  <RouteComparison
                    optimizedMetrics={optimizationResult.optimized_metrics}
                    baselineMetrics={optimizationResult.baseline_metrics}
                    improvement={optimizationResult.improvement}
                  />
                  
                  {googleMapsApiKey && optimizationResult.coordinates && (
                    <RouteMap
                      optimizedRoute={optimizationResult.coordinates.optimized}
                      baselineRoute={optimizationResult.coordinates.baseline}
                      googleMapsApiKey={googleMapsApiKey}
                    />
                  )}
                  
                  {!googleMapsApiKey && (
                    <Alert severity="warning">
                      Configure Google Maps API key to see route visualization on map.
                    </Alert>
                  )}
                </>
              )}
            </Box>
          )}
        </Container>

        {/* API Key Configuration Dialog */}
        <Dialog open={apiKeyDialogOpen} onClose={() => setApiKeyDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Configure Google Maps API Key</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Enter your Google Maps API key to enable route visualization.
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
              Get your API key from: <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer">Google Cloud Console</a>
            </Typography>
            <TextField
              fullWidth
              label="Google Maps API Key"
              value={googleMapsApiKey}
              onChange={(e) => setGoogleMapsApiKey(e.target.value)}
              placeholder="AIzaSy..."
              type="password"
              sx={{ mt: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setApiKeyDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSaveApiKey} variant="contained">Save</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </ThemeProvider>
  );
}

export default App;