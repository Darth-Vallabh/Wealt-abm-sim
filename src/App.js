// src/App.js
import React, { useState } from 'react';
import { runSimulation } from './api';
import Chart from './components/Chart';
import ControlPanel from './components/ControlPanel';

function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRun = async (config) => {
    try {
      setLoading(true);
      setError(null);
      const output = await runSimulation(config);
      setResults(output);
    } catch (err) {
      console.error('Simulation error:', err);
      setError('Simulation failed. Please check your inputs or try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center' }}>Agent-Based Wealth Simulation</h1>
      <ControlPanel onRun={handleRun} />
      {loading && <p style={{ textAlign: 'center' }}>Running simulation...</p>}
      {error && <p style={{ textAlign: 'center', color: 'red' }}>{error}</p>}
      <Chart results={results} />
    </div>
  );
}

export default App;