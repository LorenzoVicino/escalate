import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { TicketFilters, TicketStats, TicketSummary } from '../types'

export const PAGE_SIZE = 10
const REFRESH_MS = 15_000

export function useTicketQueue(filters: TicketFilters, paused: boolean) {
  const [tickets, setTickets] = useState<TicketSummary[]>([])
  const [stats, setStats] = useState<TicketStats | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [lastSyncedAt, setLastSyncedAt] = useState<number | null>(null)
  const [error, setError] = useState('')

  // Read filters through a ref so the polling effect never restarts on each keystroke.
  const filtersRef = useRef(filters)
  filtersRef.current = filters

  const load = useCallback(async (targetPage: number, options?: { silent?: boolean }) => {
    if (!options?.silent) setLoading(true)
    try {
      const active = filtersRef.current
      const [result, nextStats] = await Promise.all([
        api.listTickets(targetPage, PAGE_SIZE, active),
        api.ticketStats(active).catch(() => null),
      ])
      setTickets(result.items)
      setTotal(result.total)
      setPage(result.page)
      setStats(nextStats)
      setLastSyncedAt(Date.now())
      setError('')
    } catch {
      if (!options?.silent) setError('API unavailable')
    } finally {
      if (!options?.silent) setLoading(false)
    }
  }, [])

  const sync = useCallback(async () => {
    setSyncing(true)
    try {
      await api.syncHubspot()
    } catch {
      /* HubSpot may be unconfigured; the list refresh below still runs */
    } finally {
      setSyncing(false)
      await load(1)
    }
  }, [load])

  const serialized = JSON.stringify(filters)
  useEffect(() => { void load(1) }, [load, serialized])

  useEffect(() => {
    if (paused) return
    const id = window.setInterval(() => { void load(page, { silent: true }) }, REFRESH_MS)
    return () => window.clearInterval(id)
  }, [load, page, paused])

  return { tickets, stats, total, page, loading, syncing, lastSyncedAt, error, load, sync }
}
