import { RefreshIcon } from './Icons'

function ago(timestamp: number | null) {
  if (timestamp === null) return 'never'
  const seconds = Math.round((Date.now() - timestamp) / 1000)
  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  return `${Math.floor(seconds / 3600)}h ago`
}

export function SyncIndicator(
  { lastSyncedAt, syncing, onSync }:
  { lastSyncedAt: number | null; syncing: boolean; onSync: () => void },
) {
  return <div className="sync-indicator">
    <span>{syncing ? 'Syncing…' : `Synced ${ago(lastSyncedAt)}`}</span>
    <button onClick={onSync} disabled={syncing} aria-label="Sync HubSpot now" title="Pull new tickets from HubSpot">
      <RefreshIcon width={15} height={15} className={syncing ? 'spinning' : undefined} />
    </button>
  </div>
}
