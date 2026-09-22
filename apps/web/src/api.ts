import type { TicketInput, TicketResult, TicketSummary } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  listTickets: () => request<TicketSummary[]>('/api/v1/tickets'),
  getTicket: (id: string) => request<TicketResult>(`/api/v1/tickets/${id}`),
  createTicket: (ticket: TicketInput) => request<TicketResult>('/api/v1/tickets', {
    method: 'POST',
    body: JSON.stringify(ticket),
  }),
}

