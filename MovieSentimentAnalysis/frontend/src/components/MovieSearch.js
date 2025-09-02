import React, { useState, useEffect } from 'react';

const MovieSearch = ({ onSearch, isLoading, searchResults }) => {
  const [movieName, setMovieName] = useState('');
  const [sentiment, setSentiment] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    await onSearch(movieName, sentiment);
  };

  const handleClearSearch = () => {
    setMovieName('');
    setSentiment('');
    onSearch('', '');
  };

  return (
    <div style={{ marginBottom: '30px', padding: '20px', border: '1px solid #ddd', backgroundColor: '#f8f9fa' }}>
      <h2>Search Movies by Sentiment</h2>
      
      <form onSubmit={handleSearch} style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', alignItems: 'end' }}>
          {/* Movie Name Input */}
          <div style={{ minWidth: '200px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Movie Name:
            </label>
            <input
              type="text"
              value={movieName}
              onChange={(e) => setMovieName(e.target.value)}
              placeholder="Enter movie name..."
              disabled={isLoading}
              style={{ 
                padding: '8px 12px', 
                width: '100%', 
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            />
          </div>
          
          <div style={{ minWidth: '150px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Sentiment:
            </label>
            <select
              value={sentiment}
              onChange={(e) => setSentiment(e.target.value)}
              disabled={isLoading}
              style={{ 
                padding: '8px 12px', 
                width: '100%', 
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            >
              <option value="">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
            </select>
          </div>
          
          <div>
            <button 
              type="submit" 
              disabled={isLoading}
              style={{ 
                padding: '8px 20px', 
                backgroundColor: isLoading ? '#ccc' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoading ? 'not-allowed' : 'pointer'
              }}
            >
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </div>
          
          <div>
            <button 
              type="button"
              onClick={handleClearSearch}
              disabled={isLoading}
              style={{ 
                padding: '8px 20px', 
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoading ? 'not-allowed' : 'pointer'
              }}
            >
              Clear
            </button>
          </div>
        </div>
      </form>

      <div style={{ fontSize: '14px', color: '#666', backgroundColor: '#e9ecef', padding: '10px', borderRadius: '4px' }}>
        <p><strong>Tips:</strong></p>
        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
          <li>Leave movie name empty to search all movies</li>
          <li>Movie name search is case-insensitive and supports partial matches</li>
          <li>Use "Clear" to reset search and show all results</li>
        </ul>
      </div>

      {searchResults && (
        <div style={{ marginTop: '20px' }}>
          <h3>Search Results ({searchResults.total_count} found)</h3>
          
          <div style={{ 
            backgroundColor: '#d1ecf1', 
            padding: '10px', 
            borderRadius: '4px', 
            marginBottom: '15px',
            fontSize: '14px'
          }}>
            <strong>Search Criteria:</strong> 
            Movie: "{searchResults.search_criteria?.movie_name || 'Any'}" | 
            Sentiment: "{searchResults.search_criteria?.sentiment || 'Any'}"
          </div>

          {searchResults.results.length === 0 ? (
            <p style={{ color: '#666', fontStyle: 'italic' }}>
              No results found. Try different search criteria.
            </p>
          ) : (
            <div style={{ maxHeight: '400px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '4px' }}>
              {searchResults.results.map((result, index) => (
                <div 
                  key={index}
                  style={{ 
                    padding: '15px', 
                    borderBottom: index < searchResults.results.length - 1 ? '1px solid #eee' : 'none',
                    backgroundColor: result.sentiment === 'positive' ? '#d4edda' : '#f8d7da'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                    <h4 style={{ margin: '0', color: '#333' }}>{result.movie_name}</h4>
                    <span 
                      style={{ 
                        padding: '4px 8px', 
                        borderRadius: '12px', 
                        fontSize: '12px', 
                        fontWeight: 'bold',
                        backgroundColor: result.sentiment === 'positive' ? '#28a745' : '#dc3545',
                        color: 'white'
                      }}
                    >
                      {result.sentiment.toUpperCase()}
                    </span>
                  </div>
                  
                  <p style={{ margin: '0 0 8px 0', color: '#666' }}>
                    <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%
                  </p>
                  
                  <p style={{ 
                    margin: '0', 
                    fontSize: '14px', 
                    lineHeight: '1.4',
                    maxHeight: '60px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    <strong>Review:</strong> {result.original_text}
                  </p>
                  
                  {result.timestamp && (
                    <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#999' }}>
                      Processed: {new Date(result.timestamp).toLocaleString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MovieSearch;