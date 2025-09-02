import React, { useState, useEffect } from 'react';
import CSVUploadForm from './components/CSVUploadForm';
import MovieSearch from './components/MovieSearch';
import { uploadCSV, testBackendConnection, searchMovies } from './services/api';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  useEffect(() => {
    checkBackend();
  }, []);

  const checkBackend = async () => {
    try {
      const data = await testBackendConnection();
      setBackendStatus(`Connected (${data.ml_service_status === 'connected' ? 'ML Service: Online' : 'ML Service: Offline'})`);
    } catch (error) {
      setBackendStatus('Backend: Disconnected');
    }
  };

  const handleCSVUpload = async (file) => {
    setIsUploading(true);
    setUploadStatus('');
    
    try {
      const result = await uploadCSV(file);
      setUploadStatus(`Successfully processed ${result.processed_count} reviews from ${result.total_rows} total rows`);
      
      setTimeout(() => {
        handleSearch('', '');
      }, 1000);
      
      return { 
        success: true, 
        message: `Successfully processed ${result.processed_count} reviews` 
      };
    } catch (error) {
      setUploadStatus(' CSV processing failed');
      return { success: false, error: 'CSV processing failed' };
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async (movieName, sentiment) => {
    setIsSearching(true);
    
    try {
      const results = await searchMovies(movieName, sentiment);
      setSearchResults(results);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults({
        results: [],
        total_count: 0,
        search_criteria: { movie_name: movieName || 'Any', sentiment: sentiment || 'Any' },
        error: 'Search failed. Please try again.'
      });
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ 
        textAlign: 'center', 
        marginBottom: '30px', 
        padding: '20px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '8px',
        border: '1px solid #dee2e6'
      }}>
        <h1 style={{ color: '#333', marginBottom: '10px' }}>
          Movie Sentiment Analysis System
        </h1>
        <p style={{ color: '#666', marginBottom: '10px' }}>
          Upload CSV files with movie reviews and search for sentiment analysis results
        </p>
        <div style={{ 
          padding: '8px 16px', 
          backgroundColor: backendStatus.includes('Connected') ? '#d4edda' : '#f8d7da',
          color: backendStatus.includes('Connected') ? '#155724' : '#721c24',
          borderRadius: '4px',
          display: 'inline-block',
          fontSize: '14px'
        }}>
          Status: {backendStatus}
        </div>
      </div>

      <div style={{ marginBottom: '30px' }}>
        <CSVUploadForm 
          onUpload={handleCSVUpload}
          isLoading={isUploading}
        />
        
        {uploadStatus && (
          <div style={{ 
            marginTop: '15px', 
            padding: '10px', 
            backgroundColor: uploadStatus ? '#d4edda' : '#f8d7da',
            color: uploadStatus ? '#155724' : '#721c24',
            borderRadius: '4px',
            fontWeight: 'bold'
          }}>
            {uploadStatus}
          </div>
        )}
      </div>

      <MovieSearch 
        onSearch={handleSearch}
        isLoading={isSearching}
        searchResults={searchResults}
      />
    </div>
  );
}

export default App;