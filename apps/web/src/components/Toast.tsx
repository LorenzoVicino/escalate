import { useEffect } from 'react'

export function Toast(
  { message, actionLabel, onAction, onDismiss }:
  { message: string; actionLabel?: string; onAction?: () => void; onDismiss: () => void },
) {
  useEffect(() => {
    const id = window.setTimeout(onDismiss, 6000)
    return () => window.clearTimeout(id)
  }, [onDismiss, message])

  return <div className="toast-stack">
    <div className="toast" role="status" aria-live="polite">
      <strong>{message}</strong>
      {actionLabel && <button onClick={onAction}>{actionLabel}</button>}
    </div>
  </div>
}
