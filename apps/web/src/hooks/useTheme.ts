import { useEffect } from 'react'
import { useLocalStorage } from './useLocalStorage'

export type Theme = 'system' | 'light' | 'dark'
const ORDER: Theme[] = ['system', 'light', 'dark']

export function useTheme() {
  const [theme, setTheme] = useLocalStorage<Theme>('escalate.theme', 'system')

  useEffect(() => {
    if (theme === 'system') delete document.documentElement.dataset.theme
    else document.documentElement.dataset.theme = theme
  }, [theme])

  return {
    theme,
    cycle: () => setTheme(ORDER[(ORDER.indexOf(theme) + 1) % ORDER.length]),
  }
}
