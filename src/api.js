// src/api.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000', // adjust for prod
});

export const runSimulation = async (config) => {
  const response = await axios.post('http://127.0.0.1:8000/simulate', config);
  return response.data;
};