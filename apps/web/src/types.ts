export type TicketStatus = 'OPEN' | 'ROUTED' | 'WAITING_CONFIRMATION' | 'MANUAL_TRIAGE' | 'RESOLVED'
export type SupportTier = 'L1' | 'L2' | 'L3' | 'ENGINEERING'
export type Team = 'SUPPORT' | 'BACKEND' | 'FRONTEND' | 'DEVOPS' | 'DATABASE' | 'SECURITY' | 'MOBILE' | 'PLATFORM' | 'UNKNOWN'

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
}

export interface TicketResult extends TicketSummary {
  externalId: string | null
  description: string
  updatedAt: string
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

export interface TicketInput {
  title: string
  description: string
  customerName: string
  source: 'WEB' | 'API'
}

