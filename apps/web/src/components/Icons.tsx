import type { SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement>

const base = { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const }

export const BoltIcon = (props: IconProps) => <svg {...base} {...props}><path d="m13 2-9 12h7l-1 8 9-12h-7z" /></svg>
export const QueueIcon = (props: IconProps) => <svg {...base} {...props}><path d="M4 6h16M4 12h16M4 18h10" /></svg>
export const ChartIcon = (props: IconProps) => <svg {...base} {...props}><path d="M4 20V10m6 10V4m6 16v-7m4 7H2" /></svg>
export const SettingsIcon = (props: IconProps) => <svg {...base} {...props}><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z" /></svg>
export const PlusIcon = (props: IconProps) => <svg {...base} {...props}><path d="M12 5v14M5 12h14" /></svg>
export const ArrowIcon = (props: IconProps) => <svg {...base} {...props}><path d="m9 18 6-6-6-6" /></svg>
export const CloseIcon = (props: IconProps) => <svg {...base} {...props}><path d="m6 6 12 12M18 6 6 18" /></svg>
export const MailIcon = (props: IconProps) => <svg {...base} {...props}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></svg>
export const PhoneIcon = (props: IconProps) => <svg {...base} {...props}><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.4 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.5c.9.4 1.8.6 2.8.8a2 2 0 0 1 1.7 2Z" /></svg>
export const CalendarIcon = (props: IconProps) => <svg {...base} {...props}><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" /></svg>
export const NoteIcon = (props: IconProps) => <svg {...base} {...props}><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" /><path d="M14 3v6h6M8 13h8M8 17h5" /></svg>
export const CheckSquareIcon = (props: IconProps) => <svg {...base} {...props}><path d="M9 11l3 3 7-7" /><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9" /></svg>
export const BellIcon = (props: IconProps) => <svg {...base} {...props}><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.7 21a2 2 0 0 1-3.4 0" /></svg>
export const BellOffIcon = (props: IconProps) => <svg {...base} {...props}><path d="M13.7 21a2 2 0 0 1-3.4 0M18.6 13A17 17 0 0 0 18 8a6 6 0 0 0-9.3-5M6.3 6.3A6 6 0 0 0 6 8c0 7-3 9-3 9h14M2 2l20 20" /></svg>
export const SearchIcon = (props: IconProps) => <svg {...base} {...props}><circle cx="11" cy="11" r="7" /><path d="m21 21-4.3-4.3" /></svg>
export const RefreshIcon = (props: IconProps) => <svg {...base} {...props}><path d="M21 12a9 9 0 1 1-2.6-6.4M21 3v6h-6" /></svg>
export const SunIcon = (props: IconProps) => <svg {...base} {...props}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
export const MoonIcon = (props: IconProps) => <svg {...base} {...props}><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8" /></svg>
export const MonitorIcon = (props: IconProps) => <svg {...base} {...props}><rect x="2" y="4" width="20" height="13" rx="2" /><path d="M8 21h8M12 17v4" /></svg>
export const UserIcon = (props: IconProps) => <svg {...base} {...props}><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></svg>

