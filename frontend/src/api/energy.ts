import { http, unwrap } from './control'

export async function fetchRealtimeEnergy(params: { line: string; station_ip?: string }) {
  const { data } = await http.get('/api/energy/realtime', { params })
  return unwrap(data)
}

export async function fetchEnergyTrend(params: { line: string; station_ip?: string; period: string }) {
  const { data } = await http.get('/api/energy/trend', { params })
  return unwrap(data)
}

export async function fetchEnergyKpi(params: { line: string; station_ip?: string }) {
  const { data } = await http.get('/api/energy/kpi', { params })
  return unwrap(data)
}

export async function fetchEnergySuggestions(params: { line: string; station_ip?: string }) {
  const { data } = await http.get('/api/energy/suggestions', { params })
  return unwrap(data)
}

export async function fetchEnergyCompare(params: { line: string; station_ip?: string; period: string }) {
  const { data } = await http.get('/api/energy/compare', { params })
  return unwrap(data)
}

export async function fetchEnergyClassification(params: { line: string; station_ip?: string; period: string }) {
  const { data } = await http.get('/api/energy/classification', { params })
  return unwrap(data)
}