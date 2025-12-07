import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Checkbox,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import { PriorityHigh, Schedule } from '@mui/icons-material';
import { MailItem } from '../../types';
import { mailItemsAPI } from '../../services/api';

interface MailItemsListProps {
  refresh: boolean;
  onSelectionChange: (selected: number[]) => void;
}

const MailItemsList: React.FC<MailItemsListProps> = ({ refresh, onSelectionChange }) => {
  const [mailItems, setMailItems] = useState<MailItem[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMailItems();
  }, [refresh]);

  const fetchMailItems = async () => {
    setLoading(true);
    try {
      const response = await mailItemsAPI.getAll();
      setMailItems(response.data);
    } catch (error) {
      console.error('Failed to fetch mail items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePriority = async (item: MailItem) => {
    const newPriority = item.priority === 'urgent' ? 'regular' : 'urgent';
    try {
      await mailItemsAPI.updatePriority(item.id, newPriority);
      fetchMailItems();
    } catch (error) {
      console.error('Failed to update priority:', error);
    }
  };

  const handleSelectItem = (id: number) => {
    const newSelected = selected.includes(id)
      ? selected.filter((s) => s !== id)
      : [...selected, id];
    setSelected(newSelected);
    onSelectionChange(newSelected);
  };

  const handleSelectAll = () => {
    if (selected.length === mailItems.length) {
      setSelected([]);
      onSelectionChange([]);
    } else {
      const allIds = mailItems.map((item) => item.id);
      setSelected(allIds);
      onSelectionChange(allIds);
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading mail items...</Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          Mail Items ({mailItems.length})
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {selected.length} selected
        </Typography>
      </Box>

      {mailItems.length === 0 ? (
        <Typography color="text.secondary" textAlign="center" py={4}>
          No mail items yet. Upload a CSV or add items manually.
        </Typography>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selected.length === mailItems.length && mailItems.length > 0}
                    indeterminate={selected.length > 0 && selected.length < mailItems.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell>Tracking #</TableCell>
                <TableCell>Recipient</TableCell>
                <TableCell>Address</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Coordinates</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mailItems.map((item) => (
                <TableRow key={item.id} hover>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selected.includes(item.id)}
                      onChange={() => handleSelectItem(item.id)}
                    />
                  </TableCell>
                  <TableCell>{item.tracking_number}</TableCell>
                  <TableCell>{item.recipient_name}</TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {item.destination_address.address_line}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {item.destination_address.city}, {item.destination_address.postal_code}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={item.priority}
                      color={item.priority === 'urgent' ? 'error' : 'default'}
                      size="small"
                      icon={item.priority === 'urgent' ? <PriorityHigh /> : <Schedule />}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {item.destination_address.latitude?.toFixed(4)}, {item.destination_address.longitude?.toFixed(4)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Toggle Priority">
                      <IconButton
                        size="small"
                        onClick={() => handleTogglePriority(item)}
                        color={item.priority === 'urgent' ? 'error' : 'default'}
                      >
                        <PriorityHigh />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
};

export default MailItemsList;