// frontend/src/components/DeliveryAddressForm.jsx

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateAddress = async () => {
    const fullAddress = `${formData.address_line1}, ${formData.city}, ${formData.state} ${formData.postal_code}`;
    
    try {
      const response = await deliveryAddressAPI.validateAddress(fullAddress);
      
      if (response.data.valid) {
        setValidationStatus({
          type: 'success',
          message: 'Address validated successfully',
          coords: { lat: response.data.latitude, lng: response.data.longitude }
        });
      } else {
        setValidationStatus({
          type: 'error',
          message: 'Address not found. Please check and try again.'
        });
      }
    } catch (error) {
      setValidationStatus({
        type: 'error',
        message: 'Validation service unavailable'
      });
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);

    try {
      await deliveryAddressAPI.create(formData);
      alert('Delivery address added successfully!');
      
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
    } catch (error) {
      const errorMessage = error.response?.data 
        ? JSON.stringify(error.response.data) 
        : 'Network error. Please try again.';
      alert(`Error: ${errorMessage}`);
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
    } catch (error) {
      alert('Upload failed. Please try again.');
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
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label>Phone Number *</label>
              <input
                type="tel"
                name="recipient_phone"
                value={formData.recipient_phone}
                onChange={handleInputChange}
                placeholder="+1234567890"
                className="form-input"
              />
            </div>

            <div className="form-group full-width">
              <label>Email (Optional)</label>
              <input
                type="email"
                name="recipient_email"
                value={formData.recipient_email}
                onChange={handleInputChange}
                className="form-input"
              />
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
                className="form-input"
              />
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
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>State *</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleInputChange}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Postal Code *</label>
                <input
                  type="text"
                  name="postal_code"
                  value={formData.postal_code}
                  onChange={handleInputChange}
                  className="form-input"
                />
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
                className="form-input"
              >
                <option value="regular">Regular</option>
                <option value="urgent">Urgent</option>
              </select>
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
                    className="form-input"
                  />
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
                    className="form-input"
                  />
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