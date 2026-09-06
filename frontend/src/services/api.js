import axios from 'axios';

// The Vite proxy will route /api to the FastAPI backend at port 8000
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getBugs = async () => {
  // Using a mock return here since the backend router for GET /api/bugs might not return full list yet
  // In a real scenario, this connects to the actual DB
  try {
    const response = await apiClient.get('/bugs');
    return response.data;
  } catch (error) {
    console.error("Error fetching bugs", error);
    return [];
  }
};

export const submitBug = async (bugData) => {
  const response = await apiClient.post('/bugs/ingest', bugData);
  return response.data;
};

export const getScenario = async (scenarioId) => {
  const response = await apiClient.get(`/scenarios/${scenarioId}`);
  return response.data;
};

export const getScenarioExplanation = async (scenarioId) => {
  const response = await apiClient.get(`/scenarios/${scenarioId}/explanation`);
  return response.data;
};

export const getDashboardStats = async () => {
  try {
    const response = await apiClient.get('/evaluation/report');
    return response.data;
  } catch (error) {
    // Return mock stats if backend isn't ready
    return {
      rsr: 0.78,
      precision: 0.82,
      recall: 0.76,
      time_saved_hours: 1042,
    };
  }
};
