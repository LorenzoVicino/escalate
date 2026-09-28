import { type Operator, initialsOf } from '../hooks/useOperator'
import type { Theme } from '../hooks/useTheme'
import type { Health } from '../types'
import { BellIcon, BellOffIcon, BoltIcon, ChartIcon, MonitorIcon, MoonIcon, QueueIcon, SunIcon } from './Icons'

const THEME_ICON = { system: MonitorIcon, light: SunIcon, dark: MoonIcon }

export function Sidebar(
  { openCount, newCount, operator, onEditOperator, health, theme, onCycleTheme, muted, onToggleMute }:
  {
    openCount: number
    newCount: number
    operator: Operator | null
    onEditOperator: () => void
    health: Health | null
    theme: Theme
    onCycleTheme: () => void
    muted: boolean
    onToggleMute: () => void
  },
) {
  const ThemeIcon = THEME_ICON[theme]
  return <aside className="sidebar">
    <div className="brand"><span className="brand-mark"><BoltIcon /></span><div><strong>ESCALATE</strong><small>TRIAGE OPERATIONS</small></div></div>
    <nav aria-label="Primary">
      <button className="nav-item active"><QueueIcon />Triage queue<span className={newCount ? 'alert' : undefined}>{newCount || openCount}</span></button>
      <button className="nav-item"><ChartIcon />Analytics</button>
    </nav>
    <div className="sidebar-bottom">
      <div className="system-status">
        <span className={`pulse${health ? '' : ' offline'}`} />
        <div>
          <strong>Decision engine</strong>
          <small>{health ? `${health.provider} provider online` : 'API unreachable'}</small>
        </div>
      </div>
      <button className="nav-item" onClick={onCycleTheme}><ThemeIcon />{theme === 'system' ? 'System theme' : theme === 'light' ? 'Light theme' : 'Dark theme'}</button>
      <button className="nav-item" onClick={onToggleMute}>{muted ? <BellOffIcon /> : <BellIcon />}{muted ? 'Alerts muted' : 'Alerts on'}</button>
      <button className="operator" onClick={onEditOperator} title="Switch operator">
        <span>{operator ? initialsOf(operator.name) : '?'}</span>
        <div><strong>{operator?.name ?? 'Not identified'}</strong><small>{operator?.email ?? 'Click to choose'}</small></div>
      </button>
    </div>
  </aside>
}
