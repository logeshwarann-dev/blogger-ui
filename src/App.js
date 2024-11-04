import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [prompt, setPrompt] = useState('');
  const [blogData, setBlogData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateBlog = async () => {
    setLoading(true);
    setError(null);
    setBlogData(null);

    try {
      const response = await axios.post(
        'https://dgsc1pirbg.execute-api.us-east-1.amazonaws.com/dev/generate-blog', // Replace with your API Gateway endpoint
        { prompt }
      );
      setBlogData(response.data);
    } catch (err) {
      setError('An error occurred while generating the blog. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>AI Blog Generator Bot</h1>
      <p>Generate engaging blog content with AI!</p>

      <div className="input-section">
        <textarea
          placeholder="Enter blog topic (e.g., Difference between Data Science and Machine Learning)"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        ></textarea>
        <button onClick={handleGenerateBlog} disabled={loading || !prompt}>
          {loading ? 'Generating...' : 'Generate Blog'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {blogData && (
        <div className="blog-output">
          <h2>Generated Blog</h2>
          <p>{blogData.generated_text}</p>
          <h3>Summary</h3>
          <p>{blogData.summary}</p>
          <h3>Sentiment</h3>
          <p>{blogData.sentiment}</p>
          <h3>Category</h3>
          <p>{blogData.category}</p>
          <h3>Image</h3>
          <img src={blogData.image_url} alt="Generated Visual" />
        </div>
      )}
    </div>
  );
};

export default App;
