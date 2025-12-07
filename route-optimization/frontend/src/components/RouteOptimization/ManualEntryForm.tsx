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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material';
import { Add } from '@mui/icons-material';
import { mailItemsAPI } from '../../services/api';

interface ManualEntryFormProps {
  onSuccess: () => void;
}

const ManualEntryForm: React.FC<ManualEntryFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    tracking_number: '',
    recipient_name: '',
    address: '',
    city: 'Colombo',
    postal_code: '',
    priority: 'regular' as 'urgent' | 'regular',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await mailItemsAPI.createManual(formData);
      setSuccess('Mail item created successfully! Coordinates auto-geocoded.');
      setFormData({
        tracking_number: '',
        recipient_name: '',
        address: '',
        city: 'Colombo',
        postal_code: '',
        priority: 'regular',
      });
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create mail item');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Add Mail Item Manually
      </Typography>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Coordinates will be automatically geocoded from the address
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Tracking Number"
              value={formData.tracking_number}
              onChange={(e) => handleChange('tracking_number', e.target.value)}
              required
              placeholder="e.g., TRK001"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Recipient Name"
              value={formData.recipient_name}
              onChange={(e) => handleChange('recipient_name', e.target.value)}
              required
              placeholder="e.g., John Doe"
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Address"
              value={formData.address}
              onChange={(e) => handleChange('address', e.target.value)}
              required
              placeholder="e.g., 123 Galle Road"
              multiline
              rows={2}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="City"
              value={formData.city}
              onChange={(e) => handleChange('city', e.target.value)}
              required
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Postal Code"
              value={formData.postal_code}
              onChange={(e) => handleChange('postal_code', e.target.value)}
              required
              placeholder="e.g., 00300"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                label="Priority"
                onChange={(e) => handleChange('priority', e.target.value)}
              >
                <MenuItem value="regular">Regular</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Button
          type="submit"
          variant="contained"
          size="large"
          startIcon={loading ? <CircularProgress size={20} /> : <Add />}
          disabled={loading}
          fullWidth
          sx={{ mt: 3 }}
        >
          {loading ? 'Creating & Geocoding...' : 'Add Mail Item'}
        </Button>

        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
      </Box>
    </Paper>
  );
};

export default ManualEntryForm;