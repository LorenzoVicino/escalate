let context: AudioContext | null = null
let unlocked = false

function ensureContext(): AudioContext | null {
  if (context) return context
  const Ctor = window.AudioContext ?? (window as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
  if (!Ctor) return null
  context = new Ctor()
  return context
}

/**
 * Browsers block audio until the user has interacted with the page, so the first
 * gesture of any kind resumes the context and arms the bell.
 */
export function listenForAudioUnlock(onUnlock?: () => void): () => void {
  const unlock = () => {
    const ctx = ensureContext()
    if (!ctx) return
    void ctx.resume().then(() => {
      unlocked = true
      onUnlock?.()
    }).catch(() => undefined)
  }
  document.addEventListener('pointerdown', unlock, { once: true })
  document.addEventListener('keydown', unlock, { once: true })
  return () => {
    document.removeEventListener('pointerdown', unlock)
    document.removeEventListener('keydown', unlock)
  }
}

export function isAudioUnlocked(): boolean {
  return unlocked
}

/** Two-note sine "ding" — avoids shipping a binary asset for a 0.35s sound. */
export function playChime(): void {
  const ctx = ensureContext()
  if (!ctx || ctx.state !== 'running') return
  const start = ctx.currentTime
  for (const [index, frequency] of [880, 1318.5].entries()) {
    const at = start + index * 0.12
    const oscillator = ctx.createOscillator()
    const gain = ctx.createGain()
    oscillator.type = 'sine'
    oscillator.frequency.setValueAtTime(frequency, at)
    gain.gain.setValueAtTime(0.0001, at)
    gain.gain.exponentialRampToValueAtTime(0.18, at + 0.02)
    gain.gain.exponentialRampToValueAtTime(0.0001, at + 0.22)
    oscillator.connect(gain).connect(ctx.destination)
    oscillator.start(at)
    oscillator.stop(at + 0.24)
  }
}
