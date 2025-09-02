import React from 'react';

const ResultsDisplay = ({ results }) => {
  if (results.length === 0) {
    return (
      <div>
        <h2>Results</h2>
        <p>No results yet. Analyze a review to see results here.</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Results ({results.length})</h2>
      {results.map((result, index) => (
        <div 
          key={index}
          style={{ 
            border: '1px solid #ddd', 
            padding: '15px', 
            marginBottom: '15px',
            backgroundColor: '#f9f9f9'
          }}
        >
          <h3>{result.movie_name}</h3>
          <p><strong>Sentiment:</strong> {result.sentiment}</p>
          <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</p>
          <p><strong>Review:</strong> {result.original_text}</p>
        </div>
      ))}
    </div>
  );
};

export default ResultsDisplay;