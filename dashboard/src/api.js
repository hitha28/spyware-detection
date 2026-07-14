import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
});

export async function scanFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/scan', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getReport(scanId) {
  const response = await api.get(`/reports/${scanId}`);
  return response.data;
}

export async function listReports() {
  const response = await api.get('/reports');
  return response.data;
}

export async function runMonitor() {
  const response = await api.get('/monitor');
  return response.data;
}