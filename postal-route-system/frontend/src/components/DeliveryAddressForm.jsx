

import React, { useState } from 'react';
import { Upload, MapPin, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { deliveryAddressAPI } from '../services/api';
import './DeliveryAddressForm.css';

const DeliveryAddressForm = () => {
  const [formData, setFormData] = useState({
    recipient_name: '',
    recipient_phone: '',
    recipient_email: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    priority: 'regular',
    delivery_time_start: '',
    delivery_time_end: '',
    notes: '',
    created_by: 'Supervisor'
  });

  const [csvFile, setCsvFile] = useState(null);
  const [validationStatus, setValidationStatus] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [uploadResults, setUploadResults] = useState(null);
  const [notification, setNotification] = useState(null);
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const showNotification = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields
    if (!formData.recipient_name.trim()) {
      newErrors.recipient_name = 'Recipient name is required';
    } else if (formData.recipient_name.trim().length < 2) {
      newErrors.recipient_name = 'Name must be at least 2 characters';
    }

    if (!formData.recipient_phone.trim()) {
      newErrors.recipient_phone = 'Phone number is required';
    } else if (!/^\+?[1-9]\d{1,14}$/.test(formData.recipient_phone.replace(/[\s-()]/g, ''))) {
      newErrors.recipient_phone = 'Please enter a valid phone number (e.g., +1234567890)';
    }

    // Email validation (optional but must be valid if provided)
    if (formData.recipient_email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.recipient_email)) {
      newErrors.recipient_email = 'Please enter a valid email address';
    }

    if (!formData.address_line1.trim()) {
      newErrors.address_line1 = 'Address line 1 is required';
    } else if (formData.address_line1.trim().length < 5) {
      newErrors.address_line1 = 'Address must be at least 5 characters';
    }

    if (!formData.city.trim()) {
      newErrors.city = 'City is required';
    } else if (formData.city.trim().length < 2) {
      newErrors.city = 'City must be at least 2 characters';
    }

    if (!formData.state.trim()) {
      newErrors.state = 'State is required';
    } else if (formData.state.trim().length < 2) {
      newErrors.state = 'State must be at least 2 characters';
    }

    if (!formData.postal_code.trim()) {
      newErrors.postal_code = 'Postal code is required';
    } else if (!/^\d{5}(-\d{4})?$/.test(formData.postal_code.trim())) {
      newErrors.postal_code = 'Please enter a valid postal code (e.g., 12345 or 12345-6789)';
    }

    // Priority validation
    if (!formData.priority) {
      newErrors.priority = 'Priority is required';
    }

    // Time window validation for urgent deliveries
    if (formData.priority === 'urgent') {
      if (!formData.delivery_time_start) {
        newErrors.delivery_time_start = 'Start time is required for urgent deliveries';
      }
      if (!formData.delivery_time_end) {
        newErrors.delivery_time_end = 'End time is required for urgent deliveries';
      }
      if (formData.delivery_time_start && formData.delivery_time_end) {
        if (formData.delivery_time_start >= formData.delivery_time_end) {
          newErrors.delivery_time_end = 'End time must be after start time';
        }
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

 const validateAddress = async () => {
  const fullAddress = `${formData.address_line1}, ${formData.city}, ${formData.state} ${formData.postal_code}`;
  
  if (!formData.address_line1 || !formData.city || !formData.state || !formData.postal_code) {
    setValidationStatus({
      type: 'error',
      message: 'Please fill in all required address fields before validating.'
    });
    return;
  }

  setValidationStatus({
    type: 'info',
    message: 'Validating address...'
  });
  
  try {
    const response = await deliveryAddressAPI.validateAddress(fullAddress);
    
    if (response.data.valid) {
      setValidationStatus({
        type: 'success',
        message: 'Address validated successfully',
        coords: { 
          lat: response.data.latitude, 
          lng: response.data.longitude 
        }
      });
      
      // Auto-fill coordinates in form
      setFormData(prev => ({
        ...prev,
        latitude: response.data.latitude,
        longitude: response.data.longitude
      }));
    } else {
      setValidationStatus({
        type: 'warning',
        message: 'Address not found. You can still submit, but coordinates may not be accurate.'
      });
    }
  } catch (error) {
    console.error('Validation error:', error);
    
    // Check if it's a network error or API error
    if (error.code === 'ERR_NETWORK' || !error.response) {
      setValidationStatus({
        type: 'warning',
        message: 'Cannot connect to validation service. You can still submit the address without validation.'
      });
    } else if (error.response?.status === 429) {
      setValidationStatus({
        type: 'warning',
        message: 'Too many requests. Please wait a moment and try again.'
      });
    } else if (error.response?.status === 500) {
      setValidationStatus({
        type: 'warning',
        message: 'Validation service temporarily unavailable. You can still submit the address.'
      });
    } else {
      setValidationStatus({
        type: 'error',
        message: 'Validation failed. Please check your internet connection or try again later.'
      });
    }
  }
};

  const handleSubmit = async () => {
    // Validate form before submission
    if (!validateForm()) {
      showNotification('error', 'Please fix the errors in the form before submitting.');
      return;
    }

    setSubmitting(true);

    try {
      await deliveryAddressAPI.create(formData);
      showNotification('success', 'Delivery address added successfully!');
      
      // Reset form
      setFormData({
        recipient_name: '',
        recipient_phone: '',
        recipient_email: '',
        address_line1: '',
        address_line2: '',
        city: '',
        state: '',
        postal_code: '',
        priority: 'regular',
        delivery_time_start: '',
        delivery_time_end: '',
        notes: '',
        created_by: 'Supervisor'
      });
      setValidationStatus(null);
      setErrors({});
    } catch (error) {
      let errorMessage = 'Failed to add delivery address. Please try again.';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else {
          errorMessage = JSON.stringify(error.response.data);
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showNotification('error', errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setCsvFile(file);
    setSubmitting(true);
    
    try {
      const response = await deliveryAddressAPI.bulkUpload(file, 'Supervisor');
      setUploadResults(response.data);
      showNotification('success', `Successfully uploaded ${response.data.created} addresses!`);
    } catch (error) {
      let errorMessage = 'Upload failed. Please check your CSV file and try again.';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showNotification('error', errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const downloadTemplate = () => {
    const csvContent = 'recipient_name,recipient_phone,recipient_email,address_line1,address_line2,city,state,postal_code,priority,delivery_time_start,delivery_time_end,notes\nJohn Doe,+1234567890,john@example.com,123 Main St,,Springfield,IL,62701,urgent,09:00:00,12:00:00,Handle with care';
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'delivery_template.csv';
    a.click();
  };

  return (
    <div className="container">
      {/* Notification Popup */}
      {notification && (
        <div className={`notification ${notification.type === 'success' ? 'notification-success' : 'notification-error'}`}>
          <div className="notification-content">
            {notification.type === 'success' ? (
              <CheckCircle size={24} />
            ) : (
              <AlertCircle size={24} />
            )}
            <span>{notification.message}</span>
          </div>
          <button 
            className="notification-close" 
            onClick={() => setNotification(null)}
            aria-label="Close notification"
          >
            ×
          </button>
        </div>
      )}

      <div className="card">
        <h1 className="title">Delivery Address Management</h1>
        <p className="subtitle">Add delivery addresses individually or upload via CSV</p>

        {/* CSV Upload Section */}
        <div className="upload-section">
          <h2 className="section-title">
            <Upload className="icon" size={24} />
            Bulk Upload (CSV)
          </h2>
          
          <div className="button-group">
            <button onClick={downloadTemplate} className="btn btn-primary">
              Download CSV Template
            </button>
            
            <label className="btn btn-success">
              Choose CSV File
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </label>
          </div>

          {csvFile && (
            <p className="file-selected">Selected: {csvFile.name}</p>
          )}

          {uploadResults && (
            <div className="upload-results">
              <p className="success-text">
                ✓ {uploadResults.created} addresses uploaded successfully
              </p>
              {uploadResults.errors && uploadResults.errors.length > 0 && (
                <div className="errors">
                  <p className="error-title">Errors:</p>
                  <ul>
                    {uploadResults.errors.slice(0, 5).map((err, idx) => (
                      <li key={idx}>Row {err.row}: {JSON.stringify(err.errors || err.error)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Manual Entry Form */}
        <div className="form-section">
          <h2 className="section-title">Manual Entry</h2>

          {/* Recipient Information */}
          <div className="form-grid">
            <div className="form-group">
              <label>Recipient Name *</label>
              <input
                type="text"
                name="recipient_name"
                value={formData.recipient_name}
                onChange={handleInputChange}
                className={`form-input ${errors.recipient_name ? 'input-error' : ''}`}
              />
              {errors.recipient_name && (
                <span className="error-message">{errors.recipient_name}</span>
              )}
            </div>

            <div className="form-group">
              <label>Phone Number *</label>
              <input
                type="tel"
                name="recipient_phone"
                value={formData.recipient_phone}
                onChange={handleInputChange}
                placeholder="+1234567890"
                className={`form-input ${errors.recipient_phone ? 'input-error' : ''}`}
              />
              {errors.recipient_phone && (
                <span className="error-message">{errors.recipient_phone}</span>
              )}
            </div>

            <div className="form-group full-width">
              <label>Email (Optional)</label>
              <input
                type="email"
                name="recipient_email"
                value={formData.recipient_email}
                onChange={handleInputChange}
                className={`form-input ${errors.recipient_email ? 'input-error' : ''}`}
              />
              {errors.recipient_email && (
                <span className="error-message">{errors.recipient_email}</span>
              )}
            </div>
          </div>

          {/* Address Information */}
          <div className="form-section-spacing">
            <div className="form-group">
              <label>Address Line 1 *</label>
              <input
                type="text"
                name="address_line1"
                value={formData.address_line1}
                onChange={handleInputChange}
                className={`form-input ${errors.address_line1 ? 'input-error' : ''}`}
              />
              {errors.address_line1 && (
                <span className="error-message">{errors.address_line1}</span>
              )}
            </div>

            <div className="form-group">
              <label>Address Line 2</label>
              <input
                type="text"
                name="address_line2"
                value={formData.address_line2}
                onChange={handleInputChange}
                className="form-input"
              />
            </div>

            <div className="form-grid-3">
              <div className="form-group">
                <label>City *</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  className={`form-input ${errors.city ? 'input-error' : ''}`}
                />
                {errors.city && (
                  <span className="error-message">{errors.city}</span>
                )}
              </div>

              <div className="form-group">
                <label>State *</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleInputChange}
                  className={`form-input ${errors.state ? 'input-error' : ''}`}
                />
                {errors.state && (
                  <span className="error-message">{errors.state}</span>
                )}
              </div>

              <div className="form-group">
                <label>Postal Code *</label>
                <input
                  type="text"
                  name="postal_code"
                  value={formData.postal_code}
                  onChange={handleInputChange}
                  className={`form-input ${errors.postal_code ? 'input-error' : ''}`}
                />
                {errors.postal_code && (
                  <span className="error-message">{errors.postal_code}</span>
                )}
              </div>
            </div>

            <button onClick={validateAddress} className="btn btn-validate">
              <MapPin size={18} className="icon" />
              Validate Address
            </button>

            {validationStatus && (
              <div className={`alert ${validationStatus.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                {validationStatus.type === 'success' ? (
                  <CheckCircle className="alert-icon" size={20} />
                ) : (
                  <AlertCircle className="alert-icon" size={20} />
                )}
                <div>
                  <p>{validationStatus.message}</p>
                  {validationStatus.coords && (
                    <p className="coords-text">
                      Coordinates: {validationStatus.coords.lat}, {validationStatus.coords.lng}
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Priority and Time Windows */}
          <div className="form-grid-3">
            <div className="form-group">
              <label>Priority *</label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className={`form-input ${errors.priority ? 'input-error' : ''}`}
              >
                <option value="regular">Regular</option>
                <option value="urgent">Urgent</option>
              </select>
              {errors.priority && (
                <span className="error-message">{errors.priority}</span>
              )}
            </div>

            {formData.priority === 'urgent' && (
              <>
                <div className="form-group">
                  <label>
                    <Clock size={16} className="inline-icon" />
                    Start Time *
                  </label>
                  <input
                    type="time"
                    name="delivery_time_start"
                    value={formData.delivery_time_start}
                    onChange={handleInputChange}
                    className={`form-input ${errors.delivery_time_start ? 'input-error' : ''}`}
                  />
                  {errors.delivery_time_start && (
                    <span className="error-message">{errors.delivery_time_start}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <Clock size={16} className="inline-icon" />
                    End Time *
                  </label>
                  <input
                    type="time"
                    name="delivery_time_end"
                    value={formData.delivery_time_end}
                    onChange={handleInputChange}
                    className={`form-input ${errors.delivery_time_end ? 'input-error' : ''}`}
                  />
                  {errors.delivery_time_end && (
                    <span className="error-message">{errors.delivery_time_end}</span>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Notes */}
          <div className="form-group">
            <label>Delivery Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              className="form-input"
              placeholder="Special instructions, gate codes, etc."
            />
          </div>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="btn btn-submit"
          >
            {submitting ? 'Submitting...' : 'Add Delivery Address'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeliveryAddressForm;