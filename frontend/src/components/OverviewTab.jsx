import { useMemo } from 'react'
import { motion } from 'motion/react'
import { FileText, Copy, Download } from 'lucide-react'

export default function OverviewTab({ data, onCopyText, onExportJson, onSaveBackup }) {
  const overviewText = useMemo(() => {
    if (!data) return ''
    const lines = []
    lines.push(`VESSEL : ${data.ship || ''}`)
    lines.push(`DATE   : ${data.date || ''}  |  PORT: ${data.port || ''}`)
    lines.push(`SHIFT  : ${data.shift || ''} [${data.meal || ''}]`)
    lines.push('─'.repeat(68))
    lines.push('')

    lines.push('MAIN RESTAURANTS & STATIONS:')
    for (const v of (data.venues || [])) {
      lines.push(`  ┌ ${v.name} (Report: ${v.reportTime || '—'})`)
      for (const a of (v.assignments || [])) {
        const waiter = a.waiterName ? `${a.waiterName}` : '—'
        const attendant = a.attendantName ? ` / Attendant: ${a.attendantName}` : ''
        lines.push(`  │  • ${a.station}: ${waiter}${attendant} [${a.tables}]`)
      }
      lines.push(`  └${'─'.repeat(40)}`)
    }
    lines.push('')

    lines.push('BUFFET & SPECIALTY RESTAURANTS:')
    for (const b of (data.buffetAndVenues || [])) {
      const lead = b.lead ? ` (Lead: ${b.lead})` : ''
      lines.push(`  • ${b.name} | Timing: ${b.timing || '—'}${lead}`)
      const crew = (b.crew || []).map(c => `${c.name}${c.role ? ` (${c.role})` : ''}`).join(', ')
      if (crew) lines.push(`      Crew (${b.crew.length}): ${crew}`)
    }
    lines.push('')

    lines.push('SUB-TEAMS & SIDE DUTIES:')
    for (const s of (data.sideDuties || [])) {
      lines.push(`  • ${s.name} (Timing: ${s.timing || '—'})`)
      const crew = (s.crew || []).map(c => `${c.name}`).join(', ')
      lines.push(`      Crew: ${crew}`)
    }
    lines.push('')

    if (data.specialEvents?.length) {
      lines.push('SPECIAL EVENTS & TRAVEL TALK:')
      for (const ev of data.specialEvents) {
        lines.push(`  • ${ev.title} (${ev.location})`)
        for (const p of (ev.participants || [])) {
          lines.push(`      - ${p.name} [${p.uniform}]`)
        }
      }
      lines.push('')
    }

    if (data.sickLeave?.length) {
      lines.push('SICK LEAVE / OFF:')
      for (const sk of data.sickLeave) {
        lines.push(`  • ${sk.name}`)
      }
    }

    return lines.join('\n')
  }, [data])

  return (
    <div className="h-full flex flex-col p-4">
      {/* Top Bar */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <FileText size={14} className="text-[var(--text-subtle)]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-subtle)]">
            Structured Parsed Text Stream
          </span>
        </div>
        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onCopyText(overviewText)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold
              bg-[var(--surface-inner)] hover:bg-[var(--surface-hover)]
              border border-[var(--border-subtle)]
              text-[var(--text-primary)] transition-colors duration-150 cursor-pointer"
          >
            <Copy size={12} />
            Copy Text
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={onSaveBackup}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold
              bg-[#D1FAE5] dark:bg-[#06281D] hover:bg-[#A7F3D0] dark:hover:bg-[#047857]
              border border-[#A7F3D0] dark:border-[#047857]
              text-[#047857] dark:text-[#34D399]
              transition-colors duration-150 cursor-pointer"
            title="Save JSON backup to Save Data folder with timestamp"
          >
            <Download size={12} />
            Save to Save Data
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={onExportJson}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold
              bg-[var(--surface-inner)] hover:bg-[var(--accent-color)]
              border border-[var(--border-subtle)]
              text-[var(--text-primary)] hover:text-white
              transition-colors duration-150 cursor-pointer"
          >
            <Download size={12} />
            Export As...
          </motion.button>
        </div>
      </div>

      {/* Overview Text */}
      <div className="flex-1 min-h-0 rounded-xl border border-[var(--border-subtle)] bg-[var(--surface-inner)] overflow-auto">
        <pre className="p-4 text-xs font-mono text-[var(--text-primary)] whitespace-pre-wrap leading-relaxed select-text">
          {overviewText || 'No data loaded.'}
        </pre>
      </div>
    </div>
  )
}
