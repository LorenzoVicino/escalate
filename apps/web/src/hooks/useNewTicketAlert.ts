import { useEffect, useRef, useState } from 'react'
import { isAudioUnlocked, listenForAudioUnlock, playChime } from '../lib/audio'
import type { TicketSummary } from '../types'

/**
 * Fires when the background refresh surfaces ticket ids we have never seen.
 * The first load only seeds the set, so opening the app is never an "alert".
 * Paging or filtering would make old tickets look new, so alerts are limited
 * to the unfiltered first page.
 */
export function useNewTicketAlert(
  tickets: TicketSummary[],
  options: { muted: boolean; eligible: boolean },
) {
  const seen = useRef<Set<string>>(new Set())
  const primed = useRef(false)
  const [newCount, setNewCount] = useState(0)
  const [audioReady, setAudioReady] = useState(isAudioUnlocked())

  useEffect(() => listenForAudioUnlock(() => setAudioReady(true)), [])

  useEffect(() => {
    if (tickets.length === 0 && !primed.current) return

    if (!primed.current) {
      for (const ticket of tickets) seen.current.add(ticket.id)
      primed.current = true
      return
    }

    const fresh = tickets.filter(ticket => !seen.current.has(ticket.id))
    for (const ticket of tickets) seen.current.add(ticket.id)
    if (fresh.length === 0 || !options.eligible) return

    setNewCount(fresh.length)
    if (!options.muted) playChime()
  }, [tickets, options.muted, options.eligible])

  return { newCount, audioReady, dismiss: () => setNewCount(0) }
}
