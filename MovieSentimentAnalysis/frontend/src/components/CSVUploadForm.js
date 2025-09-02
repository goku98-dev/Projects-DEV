import React, { useState } from 'react';

const CSVUploadForm = ({ onUpload, isLoading }) => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      alert('Please select a CSV file first');
      return;
    }

    if (!selectedFile.name.endsWith('.csv')) {
      alert('Please select a valid CSV file');
      return;
    }

    const result = await onUpload(selectedFile);
    
    if (result.success) {
      alert(result.message);
      setSelectedFile(null);
      // Clear the file input
      e.target.reset();
    } else {
      alert(result.error);
    }
  };

  return (
    <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ccc' }}>
      <h2>Upload CSV File</h2>
      <form onSubmit={handleUpload}>
        <div style={{ marginBottom: '15px' }}>
          <label>Select CSV File:</label>
          <br />
          <input
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            disabled={isLoading}
            style={{ marginTop: '10px', padding: '8px' }}
          />
        </div>
        
        {selectedFile && (
          <div style={{ marginBottom: '15px', color: '#666' }}>
            <p>Selected: {selectedFile.name}</p>
            <p>Size: {(selectedFile.size / 1024).toFixed(1)} KB</p>
          </div>
        )}
        
        <button 
          type="submit" 
          disabled={isLoading || !selectedFile}
          style={{ 
            padding: '10px 20px', 
            fontSize: '16px',
            backgroundColor: isLoading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'Processing CSV...' : 'Analyze'}
        </button>
      </form>
      
      <div style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
        <p><strong>CSV Format Requirements:</strong></p>
        <ul>
          <li>Must contain columns: title, review</li>
          <li>First row should be headers</li>
          <li>Maximum file size: 100 MB</li>
        </ul>
      </div>
    </div>
  );
};

export default CSVUploadForm;