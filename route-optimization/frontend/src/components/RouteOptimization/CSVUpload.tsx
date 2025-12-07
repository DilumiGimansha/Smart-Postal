import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  CircularProgress,
  Stack,
  Button,
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import { mailItemsAPI } from '../../services/api';

interface CSVUploadProps {
  onUploadSuccess: () => void;
}

const CSVUpload: React.FC<CSVUploadProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await mailItemsAPI.uploadCSV(file);
      setSuccess(response.data.message);
      setFile(null);
      // Reset file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      onUploadSuccess();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to upload CSV');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Upload Mail Items (CSV)
      </Typography>
      
      <Stack spacing={2}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            <strong>CSV Format:</strong> tracking_number, recipient_name, address, city, postal_code, priority
          </Typography>
          <Typography variant="body2" color="info.main" gutterBottom>
            📍 Latitude/Longitude will be automatically geocoded from address
          </Typography>
        </Box>

        <Button
          variant="outlined"
          component="label"
          startIcon={<CloudUpload />}
          fullWidth
        >
          Choose CSV File
          <input
            type="file"
            hidden
            accept=".csv"
            onChange={handleFileChange}
          />
        </Button>

        {file && (
          <Alert severity="info">
            Selected: {file.name}
          </Alert>
        )}

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || loading}
          fullWidth
        >
          {loading ? <CircularProgress size={24} /> : 'Upload and Process'}
        </Button>

        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">{success}</Alert>}
      </Stack>
    </Paper>
  );
};

export default CSVUpload;