import axios from 'axios';

// Replace with your actual Render backend URL
const API = axios.create({
  baseURL: 'https://wealt-abm-sim-4.onrender.com', // <- UPDATE this URL
});

export const runSimulation = async (config) => {
  const response = await API.post('/simulate', config);
  return response.data;
};