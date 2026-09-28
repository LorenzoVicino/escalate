import { useCallback, useState } from 'react'

function read<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key)
    return raw === null ? fallback : (JSON.parse(raw) as T)
  } catch {
    return fallback
  }
}

/** Typed localStorage state. Storage can throw (private mode, blocked cookies), so every access is guarded. */
export function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => read(key, initial))

  const update = useCallback((next: T) => {
    setValue(next)
    try {
      window.localStorage.setItem(key, JSON.stringify(next))
    } catch {
      /* value still lives in React state for this session */
    }
  }, [key])

  return [value, update] as const
}
