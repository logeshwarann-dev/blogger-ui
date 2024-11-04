import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [prompt, setPrompt] = useState('');
  const [blogData, setBlogData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false); // State to toggle modal

  const handleGenerateBlog = async () => {
    setLoading(true);
    setError(null);
    setBlogData(null);

    try {
      const response = await axios.post(
        'https://dgsc1pirbg.execute-api.us-east-1.amazonaws.com/dev/generate-blog',
        { prompt }
      );
      setBlogData(response.data);
    } catch (err) {
      setError('An error occurred while generating the blog. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Toggle modal visibility
  const toggleModal = () => {
    setShowModal(!showModal);
  };

  return (
    <div className="app">
      <div className="header">
        <h1>AI Blog Generator Bot</h1>
        <button className="view-developers-button" onClick={toggleModal}>
          View Developers
        </button>
      </div>
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

      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={toggleModal}>&times;</span>
            <h2>Developers</h2>
            <p>Logeshwaran N [2023MT03135]</p>
            <p>B Pavan Kalyan [2023MT03175]</p>
            <p>Achala Rao [2023MT03162]</p>
            <p>Manisha Ganji [2023MT03130]</p>
            <p>Surya [2023MT03126]</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;



