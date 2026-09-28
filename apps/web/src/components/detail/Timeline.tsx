import { useLayoutEffect, useRef, useState } from 'react'
import { channelStyle, directionLabel } from '../../lib/channels'
import { looksLikeHtml, sanitizeHtml } from '../../lib/sanitize'
import type { TicketMessage } from '../../types'

const relative = (iso: string) => {
  const seconds = (Date.parse(iso) - Date.now()) / 1000
  const units: [Intl.RelativeTimeFormatUnit, number][] = [
    ['year', 31536000], ['month', 2592000], ['day', 86400], ['hour', 3600], ['minute', 60],
  ]
  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: 'auto' })
  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size) return formatter.format(Math.round(seconds / size), unit)
  }
  return formatter.format(Math.round(seconds), 'second')
}

function TimelineItem({ message }: { message: TicketMessage }) {
  const { icon: Icon, label, slug, directional } = channelStyle(message.channel)
  const bodyRef = useRef<HTMLDivElement>(null)
  const [overflowing, setOverflowing] = useState(false)
  const [expanded, setExpanded] = useState(false)
  const isHtml = looksLikeHtml(message.body)
  const direction = directional ? directionLabel(message.direction) : null

  useLayoutEffect(() => {
    const node = bodyRef.current
    if (node) setOverflowing(node.scrollHeight > node.clientHeight + 4)
  }, [message.body])

  return <article className="thread-item">
    <span className={`thread-node channel-${slug}`} aria-hidden="true"><Icon /></span>
    <div className="thread-body-wrap">
      <div className="thread-meta">
        <span className={`channel-pill channel-${slug}`}>{label}</span>
        {direction && <span>{direction}</span>}
        {message.author && <span>{message.author}</span>}
        <span title={new Date(message.occurredAt).toLocaleString()}>{relative(message.occurredAt)}</span>
      </div>
      {message.subject && <strong className="thread-subject">{message.subject}</strong>}
      {isHtml
        ? <div ref={bodyRef} className={`thread-body${expanded ? '' : ' clipped'}`} dangerouslySetInnerHTML={{ __html: sanitizeHtml(message.body) }} />
        : <div ref={bodyRef} className={`thread-body plain${expanded ? '' : ' clipped'}`}>{message.body}</div>}
      {overflowing && <button className="thread-more" onClick={() => setExpanded(value => !value)}>{expanded ? 'Show less' : 'Show more'}</button>}
    </div>
  </article>
}

export function Timeline({ messages }: { messages: TicketMessage[] }) {
  return <section className="panel conversation-thread">
    <div className="panel-title">
      <div><span className="eyebrow">CONTEXT</span><h2>Conversation thread</h2></div>
      <span className="record-count">{messages.length} {messages.length === 1 ? 'entry' : 'entries'}</span>
    </div>
    <div className="thread-list">{messages.map((message, index) => <TimelineItem key={`${message.channel}-${index}`} message={message} />)}</div>
  </section>
}
