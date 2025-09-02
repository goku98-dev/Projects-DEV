const API_URL = 'http://localhost:5000/api';

export const testBackendConnection = async () => {
  const response = await fetch(`${API_URL}/test`);
  return response.json();
};

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('csv_file', file);

  const response = await fetch(`${API_URL}/analyze-csv`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Failed to upload CSV');
  }

  return response.json();
};

export const fetchResults = async () => {
  const response = await fetch(`${API_URL}/results`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch results');
  }

  return response.json();
};

export const searchMovies = async (movieName = '', sentiment = '') => {
  // Build query parameters
  const params = new URLSearchParams();
  if (movieName.trim()) {
    params.append('movie_name', movieName.trim());
  }
  if (sentiment.trim()) {
    params.append('sentiment', sentiment.trim());
  }

  const response = await fetch(`${API_URL}/search?${params.toString()}`);
  
  if (!response.ok) {
    throw new Error('Failed to search movies');
  }

  return response.json();
};

export const getMoviesList = async () => {
  const response = await fetch(`${API_URL}/movies`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch movies list');
  }

  return response.json();
};

export const getSentimentSummary = async (movieName = '') => {
  const params = new URLSearchParams();
  if (movieName.trim()) {
    params.append('movie_name', movieName.trim());
  }

  const response = await fetch(`${API_URL}/summary?${params.toString()}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch sentiment summary');
  }

  return response.json();
};