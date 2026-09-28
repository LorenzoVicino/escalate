import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Health } from '../types'

export function useHealth() {
  const [health, setHealth] = useState<Health | null>(null)

  useEffect(() => {
    let active = true
    api.health().then(value => { if (active) setHealth(value) }).catch(() => {
      if (active) setHealth(null)
    })
    return () => { active = false }
  }, [])

  return health
}
