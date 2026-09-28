import '@testing-library/jest-dom/vitest'
import { afterEach, vi } from 'vitest'

// jsdom has no Web Audio; the bell must never break a test run.
class StubAudioContext {
  state = 'running'
  currentTime = 0
  destination = {}
  resume = () => Promise.resolve()
  createOscillator = () => ({
    type: 'sine',
    frequency: { setValueAtTime: () => undefined },
    connect: (node: unknown) => node,
    start: () => undefined,
    stop: () => undefined,
  })
  createGain = () => ({
    gain: { setValueAtTime: () => undefined, exponentialRampToValueAtTime: () => undefined },
    connect: (node: unknown) => node,
  })
}

vi.stubGlobal('AudioContext', StubAudioContext)

afterEach(() => {
  window.localStorage.clear()
  vi.restoreAllMocks()
})
