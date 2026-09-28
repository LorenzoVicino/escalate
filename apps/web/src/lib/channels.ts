import { CalendarIcon, CheckSquareIcon, MailIcon, NoteIcon, PhoneIcon } from '../components/Icons'

type ChannelStyle = { icon: typeof MailIcon; label: string; slug: string; directional: boolean }

const CHANNELS: Record<string, ChannelStyle> = {
  NOTE: { icon: NoteIcon, label: 'Note', slug: 'note', directional: false },
  EMAIL: { icon: MailIcon, label: 'Email', slug: 'email', directional: true },
  CALL: { icon: PhoneIcon, label: 'Call', slug: 'call', directional: true },
  MEETING: { icon: CalendarIcon, label: 'Meeting', slug: 'meeting', directional: false },
  TASK: { icon: CheckSquareIcon, label: 'Task', slug: 'task', directional: false },
}

const FALLBACK: ChannelStyle = { icon: NoteIcon, label: 'Activity', slug: 'unknown', directional: false }

export function channelStyle(channel: string): ChannelStyle {
  return CHANNELS[channel?.toUpperCase()] ?? FALLBACK
}

/** HubSpot uses values like INCOMING_EMAIL / OUTBOUND; show something a human reads. */
export function directionLabel(direction: string | null): string | null {
  if (!direction) return null
  const value = direction.toUpperCase()
  if (value.includes('INCOMING') || value.includes('INBOUND')) return 'Incoming'
  if (value.includes('OUTGOING') || value.includes('OUTBOUND')) return 'Outgoing'
  return null
}
