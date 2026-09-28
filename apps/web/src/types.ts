export type TicketStatus = 'OPEN' | 'ROUTED' | 'WAITING_CONFIRMATION' | 'MANUAL_TRIAGE' | 'RESOLVED'
export type SupportTier = 'L1' | 'L2' | 'L3' | 'ENGINEERING'
export type Team =
  | 'SUPPORT'
  | 'BACKEND'
  | 'FRONTEND'
  | 'DEVOPS'
  | 'DATABASE'
  | 'SECURITY'
  | 'MOBILE'
  | 'PLATFORM'
  | 'MIDDLEWARE'
  | 'GTSAT'
  | 'INGESTION'
  | 'UNKNOWN'

export interface Signal<T> { value: T; confidence: number }

export interface TicketSummary {
  id: string
  title: string
  customerName: string
  source: string
  status: TicketStatus
  assignedTier: SupportTier | null
  assignedTeam: Team | null
  createdAt: string
  raisedAt: string
}

export interface TicketPage {
  items: TicketSummary[]
  total: number
  page: number
  pageSize: number
}

export type Channel = 'NOTE' | 'EMAIL' | 'CALL' | 'MEETING' | 'TASK'

export interface TicketMessage {
  // HubSpot can surface engagement types we do not model yet, so keep the string fallback.
  channel: Channel | string
  direction: string | null
  author: string | null
  subject: string | null
  body: string
  occurredAt: string
}

export interface TicketStats {
  total: number
  open: number
  needsReview: number
  autoRouted: number
  byStatus: Record<string, number>
  byTier: Record<string, number>
  byTeam: Record<string, number>
}

export interface TicketFilters {
  ownerId?: string
  status?: string
  team?: string
  tier?: string
  q?: string
}

export interface Owner {
  id: string
  email: string | null
  firstName: string | null
  lastName: string | null
}

export interface Health {
  status: string
  provider: string
}

export interface TicketResult extends TicketSummary {
  externalId: string | null
  description: string
  updatedAt: string
  ownerName: string | null
  ownerEmail: string | null
  contactEmail: string | null
  messages: TicketMessage[]
  analysis: {
    category: Signal<string>
    sentiment: Signal<string>
    urgency: Signal<number>
    customerImpact: Signal<number>
    technicalComplexity: Signal<number>
    requiresDeveloper: Signal<number>
    securityRisk: Signal<number>
    suggestedTeam: Signal<Team>
    provider: string
    model: string
    processingTimeMs: number
  }
  routing: {
    supportTier: SupportTier
    team: Team
    confidence: number
    routingMode: 'AUTOMATIC' | 'REQUIRES_CONFIRMATION' | 'MANUAL_TRIAGE'
    reasons: string[]
  }
}


