import { useLocalStorage } from './useLocalStorage'

export interface Operator {
  id: string
  name: string
  email: string | null
}

export const initialsOf = (name: string) =>
  name.split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]?.toUpperCase() ?? '').join('') || '?'

export function useOperator() {
  const [operator, setOperator] = useLocalStorage<Operator | null>('escalate.operator', null)
  return { operator, setOperator }
}
