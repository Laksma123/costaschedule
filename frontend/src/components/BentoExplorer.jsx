import { useState, useMemo } from 'react'
import { motion } from 'motion/react'
import {
  Building2,
  Salad,
  Zap,
  Clock,
  PartyPopper,
  HeartPulse,
  Armchair,
  ArrowRightLeft,
  AlertTriangle,
  AlertCircle,
  Copy,
  User,
  Users,
  Star,
  Calendar,
  CheckCircle2,
} from 'lucide-react'
import ContextMenu from './ContextMenu'
import SideEditModal from './SideEditModal'
import { detectDuplicates } from '../utils/rosterUtils'

function MetricCard({ tag, value, subtitle, accentColor, delay = 0, isAlert = false, alertStyle = '' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay, ease: 'easeOut' }}
      className={`rounded-xl border p-3.5 transition-all duration-200 ${
        isAlert
          ? alertStyle
          : 'border-[var(--border-subtle)] bg-[var(--surface-inner)] hover:border-[var(--accent-border)]'
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: accentColor }} />
        <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-subtle)]">
          {tag}
        </span>
      </div>
      <div className="text-base font-extrabold leading-tight">{value}</div>
      <div className="text-[11px] mt-1 font-medium">{subtitle}</div>
    </motion.div>
  )
}

function DuplicateWarningBadge({ flagInfo }) {
  if (!flagInfo) return null
  return (
    <span
      className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9.5px] font-extrabold bg-[#FEF2F2] dark:bg-[#450A0A] border border-[#F87171] text-[#DC2626] dark:text-[#FCA5A5] animate-pulse shrink-0"
      title={flagInfo.message}
    >
      <AlertCircle size={10} />
      <span>
        {flagInfo.type === 'duplicate_id'
          ? 'DUP ID'
          : flagInfo.type === 'duplicate_name'
          ? 'DUP NAME'
          : 'TYPO MATCH'}
      </span>
    </span>
  )
}

function VenueCard({ venue, venueIndex, flaggedMap = {}, onContextMenuOpen, onEditTablesDirect }) {
  const assignments = venue.assignments || []

  const handleHeaderContextMenu = (e) => {
    e.preventDefault()
    e.stopPropagation()
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'section_header',
      title: venue.name,
      subtitle: `Report: ${venue.reportTime || '—'}`,
      canChangeTiming: true,
      canMove: false,
      targetData: {
        timing: {
          targetLocation: { type: 'venue', venueIndex },
          targetName: venue.name,
          currentTiming: venue.reportTime || '',
        },
        add_crew: {
          targetSection: { type: 'venue', venueIndex },
          sectionName: venue.name,
        },
      },
    })
  }

  const handleWaiterContextMenu = (e, a, assignmentIndex) => {
    e.preventDefault()
    e.stopPropagation()
    if (!a.waiterName) return
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'venue_waiter',
      title: `Waiter: ${a.waiterName}`,
      subtitle: `${venue.name} • ${a.station}`,
      canChangeTiming: false,
      canEditTables: true,
      targetData: {
        move: {
          sourceLocation: { type: 'venue_waiter', venueIndex, assignmentIndex },
          sourceSectionId: `venue-${venueIndex}`,
          sourceSectionName: `${venue.name} (${a.station})`,
          crew: { name: a.waiterName },
        },
        edit_crew: {
          location: { type: 'venue_waiter', venueIndex, assignmentIndex },
          crew: { name: a.waiterName },
        },
        tables: {
          venueIndex,
          assignmentIndex,
          stationName: a.station,
          venueName: venue.name,
          currentTables: a.tables || '',
        },
        delete: {
          location: { type: 'venue_waiter', venueIndex, assignmentIndex },
        },
      },
    })
  }

  const handleAttendantContextMenu = (e, a, assignmentIndex) => {
    e.preventDefault()
    e.stopPropagation()
    if (!a.attendantName) return
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'venue_attendant',
      title: `Attendant: ${a.attendantName}`,
      subtitle: `${venue.name} • ${a.station}`,
      canChangeTiming: false,
      canEditTables: true,
      targetData: {
        move: {
          sourceLocation: { type: 'venue_attendant', venueIndex, assignmentIndex },
          sourceSectionId: `venue-${venueIndex}`,
          sourceSectionName: `${venue.name} (${a.station})`,
          crew: { name: a.attendantName },
        },
        edit_crew: {
          location: { type: 'venue_attendant', venueIndex, assignmentIndex },
          crew: { name: a.attendantName },
        },
        tables: {
          venueIndex,
          assignmentIndex,
          stationName: a.station,
          venueName: venue.name,
          currentTables: a.tables || '',
        },
        delete: {
          location: { type: 'venue_attendant', venueIndex, assignmentIndex },
        },
      },
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="rounded-xl border border-[var(--border-subtle)] bg-[var(--surface-card)] overflow-hidden shadow-xs hover:border-[var(--accent-border)] transition-colors duration-150"
    >
      {/* Venue Header */}
      <div
        onContextMenu={handleHeaderContextMenu}
        className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-subtle)] bg-[var(--surface-inner)]/60 select-none cursor-context-menu"
        title="Right-click anywhere on header to Change Timing or Add Personnel"
      >
        <div className="flex items-center gap-2">
          <Building2 size={15} className="text-[var(--accent-color)]" />
          <span className="font-bold text-sm text-[var(--text-primary)]">{venue.name}</span>
          <span className="text-[9.5px] text-[var(--text-subtle)] bg-[var(--surface-badge)] px-2 py-0.5 rounded border border-[var(--border-subtle)]">
            Right-click header to edit
          </span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--accent-dim)] border border-[var(--accent-border)]">
          <Clock size={12} className="text-[var(--accent-text)]" />
          <span className="text-xs font-bold text-[var(--accent-text)]">
            Report: {venue.reportTime || '—'} • {assignments.length} Stations
          </span>
        </div>
      </div>

      {/* Station Rows */}
      <div className="divide-y divide-[var(--border-subtle)]">
        {assignments.map((a, aIdx) => {
          const waiterFlag = flaggedMap[a.waiterName]
          const attendantFlag = flaggedMap[a.attendantName]

          return (
            <div
              key={aIdx}
              className={`group flex items-center justify-between gap-3 px-4 py-2.5 text-xs transition-colors ${
                aIdx % 2 === 0 ? 'bg-[var(--surface-inner)]/30' : 'bg-[var(--surface-card)]'
              } hover:bg-[var(--surface-hover)]`}
            >
              {/* Station Pill & Crew */}
              <div className="flex items-center gap-3 min-w-0 flex-1 flex-wrap">
                <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-[#E0F2FE] dark:bg-[#092535] border border-[#BAE6FD] dark:border-[#0C4A6E] text-xs font-bold text-[#0284C7] dark:text-[#38BDF8] min-w-[34px] justify-center shrink-0">
                  {a.station}
                </span>

                {/* Waiter */}
                <div
                  onContextMenu={(e) => handleWaiterContextMenu(e, a, aIdx)}
                  className={`flex items-center gap-1.5 px-2 py-1 rounded-lg border transition-all cursor-context-menu ${
                    waiterFlag
                      ? 'bg-[#FEF2F2] dark:bg-[#2B0E11] border-[#F87171] text-[#991B1B] dark:text-[#FCA5A5]'
                      : a.waiterName
                      ? 'bg-[var(--surface-card)] border-[var(--border-subtle)] hover:border-[var(--accent-border)] text-[var(--text-primary)]'
                      : 'border-dashed border-[var(--border-subtle)] text-[var(--text-subtle)]'
                  }`}
                  title={waiterFlag ? waiterFlag.message : 'Right-click to Move or Edit Waiter'}
                >
                  <User size={13} className="text-[#0071A3] shrink-0" />
                  {a.waiterName ? (
                    <span className="font-bold">
                      {a.waiterName}
                    </span>
                  ) : (
                    <span className="italic text-[11px]">Empty Waiter</span>
                  )}
                  {waiterFlag && <DuplicateWarningBadge flagInfo={waiterFlag} />}
                  {a.waiterName && (
                    <button
                      onClick={(e) => handleWaiterContextMenu(e, a, aIdx)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 ml-1 rounded hover:bg-[var(--surface-hover)] text-[var(--text-subtle)] transition-opacity cursor-pointer"
                    >
                      <ArrowRightLeft size={11} />
                    </button>
                  )}
                </div>

                {/* Attendant */}
                {a.attendantName ? (
                  <div
                    onContextMenu={(e) => handleAttendantContextMenu(e, a, aIdx)}
                    className={`flex items-center gap-1.5 px-2 py-1 rounded-lg border transition-all cursor-context-menu ${
                      attendantFlag
                        ? 'bg-[#FEF2F2] dark:bg-[#2B0E11] border-[#F87171] text-[#991B1B] dark:text-[#FCA5A5]'
                        : 'bg-[var(--surface-card)] border-[var(--border-subtle)] hover:border-[var(--accent-border)] text-[var(--text-secondary)]'
                    }`}
                    title={attendantFlag ? attendantFlag.message : 'Right-click to Move or Edit Attendant'}
                  >
                    <Users size={13} className="text-[var(--text-subtle)] shrink-0" />
                    <span className="font-medium">
                      Att: {a.attendantName}
                    </span>
                    {attendantFlag && <DuplicateWarningBadge flagInfo={attendantFlag} />}
                    <button
                      onClick={(e) => handleAttendantContextMenu(e, a, aIdx)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 ml-1 rounded hover:bg-[var(--surface-hover)] text-[var(--text-subtle)] transition-opacity cursor-pointer"
                    >
                      <ArrowRightLeft size={11} />
                    </button>
                  </div>
                ) : null}
              </div>

              {/* Tables Badge (Interactive) */}
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() =>
                    onEditTablesDirect({
                      venueIndex,
                      assignmentIndex: aIdx,
                      stationName: a.station,
                      venueName: venue.name,
                      currentTables: a.tables || '',
                    })
                  }
                  onContextMenu={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    onEditTablesDirect({
                      venueIndex,
                      assignmentIndex: aIdx,
                      stationName: a.station,
                      venueName: venue.name,
                      currentTables: a.tables || '',
                    })
                  }}
                  className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold border transition-all cursor-pointer ${
                    a.tables
                      ? 'bg-[#FEF3C7] dark:bg-[#2B1D08] border-[#FDE68A] dark:border-[#92400E] text-[#D97706] dark:text-[#F59E0B] hover:opacity-85'
                      : 'bg-[var(--surface-inner)] border-dashed border-[var(--border-subtle)] text-[var(--text-subtle)] hover:border-[var(--accent-border)]'
                  }`}
                  title="Click or right-click to edit tables"
                >
                  <Armchair size={11} />
                  <span>{a.tables ? a.tables : '+ Tables'}</span>
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}

function BuffetCard({ item, buffetIndex, flaggedMap = {}, onContextMenuOpen }) {
  const crew = item.crew || []

  const handleHeaderContextMenu = (e) => {
    e.preventDefault()
    e.stopPropagation()
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'section_header',
      title: item.name,
      subtitle: `Timing: ${item.timing || '—'}`,
      canChangeTiming: true,
      canMove: false,
      targetData: {
        timing: {
          targetLocation: { type: 'buffet', buffetIndex },
          targetName: item.name,
          currentTiming: item.timing || '',
        },
        add_crew: {
          targetSection: { type: 'buffet', buffetIndex },
          sectionName: item.name,
        },
      },
    })
  }

  const handleCrewContextMenu = (e, c, crewIndex) => {
    e.preventDefault()
    e.stopPropagation()
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'buffet_crew',
      title: `Crew: ${c.name}`,
      subtitle: `${item.name}${c.role ? ` • ${c.role}` : ''}`,
      canChangeTiming: Boolean(c.role && c.role.includes(':')),
      targetData: {
        move: {
          sourceLocation: { type: 'buffet', buffetIndex, crewIndex },
          sourceSectionId: `buffet-${buffetIndex}`,
          sourceSectionName: item.name,
          crew: { name: c.name, role: c.role },
        },
        timing: {
          targetLocation: { type: 'crew_role', buffetIndex, crewIndex },
          targetName: `Role Timing: ${c.name}`,
          currentTiming: c.role || '',
        },
        edit_crew: {
          location: { type: 'buffet', buffetIndex, crewIndex },
          crew: { name: c.name, role: c.role },
        },
        delete: {
          location: { type: 'buffet', buffetIndex, crewIndex },
        },
      },
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="rounded-xl border border-[var(--border-subtle)] bg-[var(--surface-card)] overflow-hidden shadow-xs hover:border-[var(--accent-border)] transition-colors duration-150"
    >
      <div
        onContextMenu={handleHeaderContextMenu}
        className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-subtle)] bg-[var(--surface-inner)]/60 select-none cursor-context-menu"
        title="Right-click anywhere on header to Change Timing or Add Personnel"
      >
        <div className="flex items-center gap-2 flex-wrap">
          <Salad size={15} className="text-[#10B981]" />
          <span className="font-bold text-sm text-[var(--text-primary)]">{item.name}</span>
          {item.lead && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#FEF3C7] dark:bg-[#2B1D08] border border-[#FDE68A] dark:border-[#92400E] text-xs font-semibold text-[#D97706] dark:text-[#F59E0B]">
              <Star size={11} className="shrink-0" />
              <span>Lead: {item.lead}</span>
            </span>
          )}
          <span className="text-[9.5px] text-[var(--text-subtle)] bg-[var(--surface-badge)] px-2 py-0.5 rounded border border-[var(--border-subtle)]">
            Right-click header to edit
          </span>
        </div>
        <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--text-secondary)] px-3 py-1 rounded-full bg-[var(--surface-inner)] border border-[var(--border-subtle)]">
          <Clock size={11} className="shrink-0 text-[var(--text-subtle)]" />
          <span>{item.timing || '—'} • {crew.length} Crew</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 px-4 py-3">
        {crew.map((c, ci) => {
          const flag = flaggedMap[c.name]
          return (
            <span
              key={ci}
              onContextMenu={(e) => handleCrewContextMenu(e, c, ci)}
              className={`group inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs transition-all cursor-context-menu select-none ${
                flag
                  ? 'bg-[#FEF2F2] dark:bg-[#2B0E11] border-[#F87171] text-[#991B1B] dark:text-[#FCA5A5]'
                  : 'bg-[var(--surface-inner)] border-[var(--border-subtle)] hover:border-[var(--accent-border)] hover:bg-[var(--surface-hover)] text-[var(--text-primary)]'
              }`}
              title={flag ? flag.message : 'Right-click to Move or Edit'}
            >
              <span className="font-semibold">
                {c.name}
              </span>
              {c.role && (
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-[var(--accent-dim)] text-[var(--accent-text)] font-medium">
                  {c.role}
                </span>
              )}
              {flag && <DuplicateWarningBadge flagInfo={flag} />}
              <button
                onClick={(e) => handleCrewContextMenu(e, c, ci)}
                className="opacity-0 group-hover:opacity-100 p-0.5 rounded text-[var(--text-subtle)] hover:text-[var(--text-primary)] transition-opacity cursor-pointer"
              >
                <ArrowRightLeft size={11} />
              </button>
            </span>
          )
        })}
        {crew.length === 0 && (
          <span className="text-xs text-[var(--text-subtle)] italic py-1">
            No crew assigned. Right-click header to add personnel.
          </span>
        )}
      </div>
    </motion.div>
  )
}

function SideDutyCard({ item, sideDutyIndex, flaggedMap = {}, onContextMenuOpen }) {
  const crew = item.crew || []

  const handleHeaderContextMenu = (e) => {
    e.preventDefault()
    e.stopPropagation()
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'section_header',
      title: item.name,
      subtitle: `Timing: ${item.timing || '—'}`,
      canChangeTiming: true,
      canMove: false,
      targetData: {
        timing: {
          targetLocation: { type: 'sideDuty', sideDutyIndex },
          targetName: item.name,
          currentTiming: item.timing || '',
        },
        add_crew: {
          targetSection: { type: 'sideDuty', sideDutyIndex },
          sectionName: item.name,
        },
      },
    })
  }

  const handleCrewContextMenu = (e, c, crewIndex) => {
    e.preventDefault()
    e.stopPropagation()
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'side_crew',
      title: `Crew: ${c.name}`,
      subtitle: item.name,
      canChangeTiming: false,
      targetData: {
        move: {
          sourceLocation: { type: 'sideDuty', sideDutyIndex, crewIndex },
          sourceSectionId: `side-${sideDutyIndex}`,
          sourceSectionName: item.name,
          crew: { name: c.name },
        },
        edit_crew: {
          location: { type: 'sideDuty', sideDutyIndex, crewIndex },
          crew: { name: c.name },
        },
        delete: {
          location: { type: 'sideDuty', sideDutyIndex, crewIndex },
        },
      },
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="rounded-xl border border-[var(--border-subtle)] bg-[var(--surface-card)] overflow-hidden shadow-xs hover:border-[var(--accent-border)] transition-colors duration-150"
    >
      <div
        onContextMenu={handleHeaderContextMenu}
        className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-subtle)] bg-[var(--surface-inner)]/60 select-none cursor-context-menu"
        title="Right-click anywhere on header to Change Timing or Add Personnel"
      >
        <div className="flex items-center gap-2">
          <Zap size={15} className="text-[#7C3AED] dark:text-[#A855F7]" />
          <span className="font-bold text-sm text-[var(--text-primary)]">{item.name}</span>
          <span className="text-[9.5px] text-[var(--text-subtle)] bg-[var(--surface-badge)] px-2 py-0.5 rounded border border-[var(--border-subtle)]">
            Right-click header to edit
          </span>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EDE9FE] dark:bg-[#230F38] border border-[#DDD6FE] dark:border-[#5B21B6] text-xs font-semibold text-[#7C3AED] dark:text-[#A855F7]">
          <Clock size={11} className="shrink-0" />
          <span>{item.timing || '—'} • {crew.length} Crew</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 px-4 py-3">
        {crew.map((c, ci) => {
          const flag = flaggedMap[c.name]
          return (
            <span
              key={ci}
              onContextMenu={(e) => handleCrewContextMenu(e, c, ci)}
              className={`group inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs transition-all cursor-context-menu select-none ${
                flag
                  ? 'bg-[#FEF2F2] dark:bg-[#2B0E11] border-[#F87171] text-[#991B1B] dark:text-[#FCA5A5]'
                  : 'bg-[var(--surface-inner)] border-[var(--border-subtle)] hover:border-[var(--accent-border)] hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
              }`}
              title={flag ? flag.message : 'Right-click to Move or Edit'}
            >
              <span className="font-medium">
                {c.name}
              </span>
              {flag && <DuplicateWarningBadge flagInfo={flag} />}
              <button
                onClick={(e) => handleCrewContextMenu(e, c, ci)}
                className="opacity-0 group-hover:opacity-100 p-0.5 rounded text-[var(--text-subtle)] hover:text-[var(--text-primary)] transition-opacity cursor-pointer"
              >
                <ArrowRightLeft size={11} />
              </button>
            </span>
          )
        })}
      </div>
    </motion.div>
  )
}

function SpecialEventsCard({ events, onContextMenuOpen }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="rounded-xl border border-[var(--border-subtle)] bg-[var(--surface-card)] overflow-hidden shadow-xs"
    >
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--border-subtle)] bg-[var(--surface-inner)]/60">
        <PartyPopper size={15} className="text-[#D97706] dark:text-[#F59E0B]" />
        <span className="font-bold text-sm text-[#D97706] dark:text-[#F59E0B]">
          SPECIAL EVENTS & TRAVEL TALK
        </span>
      </div>
      <div className="p-4 space-y-3">
        {events.map((ev, ei) => (
          <div key={ei} className="rounded-lg bg-[var(--surface-inner)] border border-[var(--border-subtle)] p-3">
            <div className="font-bold text-sm text-[var(--text-primary)] mb-2 flex items-center gap-1.5">
              <Calendar size={13} className="text-[#0071A3] shrink-0" />
              <span>{ev.title} — {ev.location}</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(ev.participants || []).map((p, pi) => (
                <span
                  key={pi}
                  onContextMenu={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    onContextMenuOpen({
                      x: e.clientX,
                      y: e.clientY,
                      targetType: 'special_event_crew',
                      title: `Participant: ${p.name}`,
                      subtitle: `${ev.title} [${p.uniform}]`,
                      canChangeTiming: false,
                      targetData: {
                        move: {
                          sourceLocation: { type: 'specialEvent', eventIndex: ei, pIndex: pi },
                          sourceSectionId: 'special-event',
                          sourceSectionName: ev.title,
                          crew: { name: p.name },
                        },
                        edit_crew: {
                          location: { type: 'specialEvent', eventIndex: ei, pIndex: pi },
                          crew: { name: p.name, role: p.uniform },
                        },
                        delete: {
                          location: { type: 'specialEvent', eventIndex: ei, pIndex: pi },
                        },
                      },
                    })
                  }}
                  className="px-2 py-0.5 rounded-md bg-[var(--surface-card)] border border-[var(--border-subtle)] text-[10px] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-border)] cursor-context-menu"
                >
                  {p.name} [{p.uniform}]
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

function SickLeaveCard({ sickList, flaggedMap = {}, onContextMenuOpen }) {
  const handleHeaderContextMenu = (e) => {
    e.preventDefault()
    e.stopPropagation()
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'section_header',
      title: 'Sick Leave / Off Duty',
      subtitle: `${sickList.length} Personnel Currently Off Duty`,
      canChangeTiming: false,
      canMove: false,
      isSickLeave: true,
      targetData: {
        add_crew: {
          targetSection: { type: 'sickLeave' },
          sectionName: 'Sick Leave / Off Duty',
        },
      },
    })
  }

  const handleSickContextMenu = (e, sk, sickIndex) => {
    e.preventDefault()
    e.stopPropagation()
    onContextMenuOpen({
      x: e.clientX,
      y: e.clientY,
      targetType: 'sick_crew',
      title: `Sick / Off: ${sk.name}`,
      subtitle: 'Right-click to Move back to active outlet',
      canChangeTiming: false,
      isSickLeave: true,
      targetData: {
        move: {
          sourceLocation: { type: 'sickLeave', sickIndex },
          sourceSectionId: 'sick-leave',
          sourceSectionName: 'Sick Leave / Off Duty',
          crew: { name: sk.name },
        },
        edit_crew: {
          location: { type: 'sickLeave', sickIndex },
          crew: { name: sk.name },
        },
        delete: {
          location: { type: 'sickLeave', sickIndex },
        },
      },
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="rounded-xl border border-[var(--border-subtle)] bg-[var(--surface-card)] overflow-hidden shadow-xs hover:border-[#FECDD3] dark:hover:border-[#881337] transition-colors duration-150"
    >
      <div
        onContextMenu={handleHeaderContextMenu}
        className="flex items-center justify-between px-4 py-3 border-b border-[var(--border-subtle)] bg-[var(--surface-inner)]/60 select-none cursor-context-menu"
        title="Right-click anywhere on header to Add Personnel to Sick Leave"
      >
        <div className="flex items-center gap-2">
          <HeartPulse size={15} className="text-[#E11D48] dark:text-[#FB7185]" />
          <span className="font-bold text-sm text-[#E11D48] dark:text-[#FB7185]">
            SICK LEAVE / OFF DUTY
          </span>
          <span className="text-[9.5px] text-[var(--text-subtle)] bg-[var(--surface-badge)] px-2 py-0.5 rounded border border-[var(--border-subtle)]">
            Right-click header to add • Right-click crew to Move
          </span>
        </div>
        <div className="text-xs font-bold text-[#E11D48] dark:text-[#FB7185] px-2.5 py-0.5 rounded-full bg-[#FFE4E6] dark:bg-[#2E0E15] border border-[#FECDD3] dark:border-[#881337]">
          {sickList.length} Personnel
        </div>
      </div>

      <div className="flex flex-wrap gap-2 px-4 py-3">
        {sickList.map((sk, si) => {
          const flag = flaggedMap[sk.name]
          return (
            <span
              key={si}
              onContextMenu={(e) => handleSickContextMenu(e, sk, si)}
              className="group inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FFE4E6] dark:bg-[#2E0E15] border border-[#FECDD3] dark:border-[#881337] text-xs font-bold text-[#E11D48] dark:text-[#FB7185] hover:shadow-sm transition-all cursor-context-menu select-none"
              title={flag ? flag.message : 'Right-click to Move back to outlet or Edit'}
            >
              <span>{sk.name}</span>
              {flag && <DuplicateWarningBadge flagInfo={flag} />}
              <button
                onClick={(e) => handleSickContextMenu(e, sk, si)}
                className="opacity-0 group-hover:opacity-100 p-0.5 rounded text-[#E11D48] dark:text-[#FB7185] hover:bg-[#FECDD3]/50 transition-opacity cursor-pointer"
                title="Actions"
              >
                <ArrowRightLeft size={11} />
              </button>
            </span>
          )
        })}
        {sickList.length === 0 && (
          <span className="text-xs text-[var(--text-subtle)] italic py-1">
            No sick leave crew.
          </span>
        )}
      </div>
    </motion.div>
  )
}

export default function BentoExplorer({
  data,
  telemetry,
  searchQuery,
  activeFilter,
  payload,
  targetCrewCount = '',
  theme = 'sakura',
  onMoveCrew,
  onUpdateTiming,
  onUpdateTables,
  onUpdateCrewDetails,
  onAddCrew,
  onDeleteCrew,
}) {
  // Context Menu State
  const [contextMenu, setContextMenu] = useState({ isOpen: false, x: 0, y: 0 })

  // Side Modal State
  const [modalState, setModalState] = useState({
    isOpen: false,
    mode: 'move',
    target: null,
  })

  // Duplicate & Typo Detection
  const duplicateReport = useMemo(() => detectDuplicates(data), [data])
  const flaggedMap = duplicateReport.flaggedCrewMap || {}

  const currentCrew = telemetry?.crewCount || 0
  const targetNum = parseInt(targetCrewCount, 10)
  const hasTarget = !isNaN(targetNum) && targetNum > 0

  const isDeficit = hasTarget && currentCrew < targetNum
  const isSurplus = hasTarget && currentCrew > targetNum
  const isMatch = hasTarget && currentCrew === targetNum

  const deficitCount = isDeficit ? targetNum - currentCrew : 0
  const surplusCount = isSurplus ? currentCrew - targetNum : 0

  // Deficit / Surplus alert styling per theme
  const getBentoAlertStyles = () => {
    if (isDeficit) {
      if (theme === 'dark') return 'bg-[#2A1504] border-[#B45309] text-[#FBBF24] ring-2 ring-[#F59E0B]/60 animate-pulse'
      if (theme === 'sakura') return 'bg-[#FFE4EE] border-[#F43F5E] text-[#9F1239] ring-2 ring-[#F43F5E]/60 animate-pulse'
      return 'bg-[#FEF3C7] border-[#F59E0B] text-[#B45309] ring-2 ring-[#F59E0B]/60 animate-pulse'
    }
    if (isSurplus) {
      if (theme === 'dark') return 'bg-[#1C1635] border-[#9333EA] text-[#D8B4FE] ring-2 ring-[#A855F7]/60 animate-pulse'
      if (theme === 'sakura') return 'bg-[#F3E8FF] border-[#C084FC] text-[#7E22CE] ring-2 ring-[#A855F7]/60 animate-pulse'
      return 'bg-[#F3E8FF] border-[#A855F7] text-[#6B21A8] ring-2 ring-[#A855F7]/60 animate-pulse'
    }
    if (isMatch) {
      if (theme === 'dark') return 'bg-[#06281D] border-[#059669] text-[#34D399]'
      if (theme === 'sakura') return 'bg-[#ECFDF5] border-[#10B981] text-[#047857]'
      return 'bg-[#D1FAE5] border-[#10B981] text-[#065F46]'
    }
    return ''
  }

  const filteredData = useMemo(() => {
    if (!data) return null
    const q = (searchQuery || '').toLowerCase()

    const filterVenues = (venues) => {
      if (!venues) return []
      return venues
        .map((v, vIdx) => ({
          ...v,
          originalIndex: vIdx,
          assignments: (v.assignments || [])
            .map((a, aIdx) => ({ ...a, originalIndex: aIdx }))
            .filter(
              (a) =>
                !q ||
                (a.station || '').toLowerCase().includes(q) ||
                (a.waiterName || '').toLowerCase().includes(q) ||
                (a.attendantName || '').toLowerCase().includes(q) ||
                (a.tables || '').toLowerCase().includes(q)
            ),
        }))
        .filter((v) => v.assignments.length > 0 || !q)
    }

    const filterCrew = (items, type) => {
      if (!items) return []
      return items
        .map((item, itemIdx) => ({
          ...item,
          originalIndex: itemIdx,
          crew: (item.crew || [])
            .map((c, cIdx) => ({ ...c, originalIndex: cIdx }))
            .filter(
              (c) =>
                !q ||
                (c.name || '').toLowerCase().includes(q) ||
                (item.name || '').toLowerCase().includes(q)
            ),
        }))
        .filter((item) => item.crew.length > 0 || !q)
    }

    return {
      venues: filterVenues(data.venues),
      buffets: filterCrew(data.buffetAndVenues, 'buffet'),
      sideDuties: filterCrew(data.sideDuties, 'sideDuty'),
      specialEvents: data.specialEvents || [],
      sickLeave: data.sickLeave || [],
    }
  }, [data, searchQuery])

  if (!data) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--text-subtle)]">
        <p className="text-xs">
          No schedule loaded. Click <strong>Browse Roster</strong> to open an Excel file.
        </p>
      </div>
    )
  }

  const t = telemetry || {}

  const handleOpenContextMenu = (cfg) => {
    setContextMenu({
      isOpen: true,
      ...cfg,
    })
  }

  const handleCloseContextMenu = () => {
    setContextMenu((prev) => ({ ...prev, isOpen: false }))
  }

  const handleContextMenuAction = (action) => {
    const targetData = contextMenu.targetData || {}

    if (action === 'move') {
      setModalState({
        isOpen: true,
        mode: 'move',
        target: targetData.move,
      })
    } else if (action === 'move_to_sick') {
      if (targetData.move && onMoveCrew) {
        onMoveCrew(
          targetData.move.sourceLocation,
          { type: 'sickLeave' },
          targetData.move.crew
        )
      }
    } else if (action === 'timing') {
      setModalState({
        isOpen: true,
        mode: 'timing',
        target: targetData.timing,
      })
    } else if (action === 'tables') {
      setModalState({
        isOpen: true,
        mode: 'tables',
        target: targetData.tables,
      })
    } else if (action === 'edit_crew') {
      setModalState({
        isOpen: true,
        mode: 'edit_crew',
        target: targetData.edit_crew,
      })
    } else if (action === 'add_crew') {
      setModalState({
        isOpen: true,
        mode: 'add_crew',
        target: targetData.add_crew,
      })
    } else if (action === 'delete') {
      if (targetData.delete && onDeleteCrew) {
        onDeleteCrew(targetData.delete.location)
      }
    }

    handleCloseContextMenu()
  }

  const handleEditTablesDirect = (tablesConfig) => {
    setModalState({
      isOpen: true,
      mode: 'tables',
      target: tablesConfig,
    })
  }

  return (
    <div className="p-4 space-y-4 relative">
      {/* 4 Metrics Cards */}
      <div className="grid grid-cols-4 gap-3">
        <MetricCard
          tag="Port & Meal"
          value={`${data.port || '—'} • ${data.meal || 'LUNCH'}`}
          subtitle={data.date || '—'}
          accentColor="#38BDF8"
          delay={0}
        />
        <MetricCard
          tag={
            isDeficit
              ? `ROSTER DEFICIT (-${deficitCount})`
              : isSurplus
              ? `ROSTER SURPLUS (+${surplusCount})`
              : isMatch
              ? `ROSTER COMPLETE`
              : 'Active Roster'
          }
          value={`${currentCrew} Crew Members`}
          subtitle={
            isDeficit
              ? `Missing ${deficitCount} of ${targetNum} target crew!`
              : isSurplus
              ? `+${surplusCount} Extra beyond target ${targetNum} (check for duplicates!)`
              : hasTarget
              ? `Perfect match! All ${targetNum} crew accounted for`
              : `${t.sectionCount || 0} Duty Sections`
          }
          accentColor={isDeficit ? '#F59E0B' : isSurplus ? '#A855F7' : isMatch ? '#10B981' : 'var(--accent-color)'}
          delay={0.05}
          isAlert={isDeficit || isSurplus || isMatch}
          alertStyle={getBentoAlertStyles()}
        />
        <MetricCard
          tag="Dining Stations"
          value={`${t.stationCount || 0} Active Tables`}
          subtitle={`${(data.venues || []).length} Restaurant Venues`}
          accentColor="#F59E0B"
          delay={0.1}
        />
        <MetricCard
          tag="Stream Encoding"
          value={`${(t.payloadChars || 0).toLocaleString()} Chars`}
          subtitle={`${(t.b64Bytes || 0).toLocaleString()} Bytes Base64`}
          accentColor="#10B981"
          delay={0.15}
        />
      </div>

      {/* Duplicate / Typo Alert Banner (If duplicates detected) */}
      {duplicateReport.hasDuplicates && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3.5 rounded-xl bg-[#FEF2F2] dark:bg-[#2B0E11] border border-[#FCA5A5] dark:border-[#991B1B] text-[#991B1B] dark:text-[#FCA5A5] shadow-sm space-y-2"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle size={16} className="text-[#DC2626] dark:text-[#F87171] shrink-0" />
              <span className="text-xs font-bold uppercase tracking-wider">
                Schedule Quality Alert: {duplicateReport.totalIssues} Potential Duplicate(s) / Typos Detected
              </span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FEE2E2] dark:bg-[#450A0A] font-extrabold text-[#DC2626] dark:text-[#F87171]">
              Attention Required
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 pt-1 text-[11px]">
            {duplicateReport.idDuplicates.map((d, i) => (
              <div key={`id-warn-${i}`} className="p-2 rounded-lg bg-white/60 dark:bg-black/40 border border-[#FECDD3] dark:border-[#881337]">
                <div className="font-bold text-[#DC2626] dark:text-[#F87171] flex items-center gap-1">
                  <span>Duplicate ID: #{d.id}</span>
                </div>
                <div className="text-[10px] opacity-90 truncate mt-0.5">
                  Names: {d.names.join(' / ')}
                </div>
                <div className="text-[9.5px] opacity-75 truncate mt-0.5">
                  Duties: {d.locations.join(' • ')}
                </div>
              </div>
            ))}

            {duplicateReport.nameDuplicates.map((d, i) => (
              <div key={`name-warn-${i}`} className="p-2 rounded-lg bg-white/60 dark:bg-black/40 border border-[#FECDD3] dark:border-[#881337]">
                <div className="font-bold text-[#DC2626] dark:text-[#F87171] flex items-center gap-1">
                  <span>Duplicate Name: {d.cleanName}</span>
                </div>
                <div className="text-[10px] opacity-90 truncate mt-0.5">
                  Appears in {d.count} different duties
                </div>
                <div className="text-[9.5px] opacity-75 truncate mt-0.5">
                  {d.locations.join(' • ')}
                </div>
              </div>
            ))}

            {duplicateReport.fuzzyDuplicates.map((d, i) => (
              <div key={`fuz-warn-${i}`} className="p-2 rounded-lg bg-white/60 dark:bg-black/40 border border-[#FED7AA] dark:border-[#7C2D12] text-[#9A3412] dark:text-[#FDBA74]">
                <div className="font-bold flex items-center gap-1">
                  <span>Typo Match:</span>
                </div>
                <div className="text-[10px] truncate mt-0.5 font-mono">
                  "{d.name1}" ≈ "{d.name2}"
                </div>
                <div className="text-[9.5px] opacity-80 truncate mt-0.5">
                  {d.locations.join(' vs ')}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Main Dining Venue Cards */}
      {(activeFilter === 'ALL' || activeFilter === 'MAIN DINING') &&
        filteredData.venues.map((v) => (
          <VenueCard
            key={`venue-${v.originalIndex}`}
            venue={v}
            venueIndex={v.originalIndex}
            flaggedMap={flaggedMap}
            onContextMenuOpen={handleOpenContextMenu}
            onEditTablesDirect={handleEditTablesDirect}
          />
        ))}

      {/* Buffet Cards */}
      {(activeFilter === 'ALL' || activeFilter === 'BUFFET & OUTLETS') &&
        filteredData.buffets.map((b) => (
          <BuffetCard
            key={`buffet-${b.originalIndex}`}
            item={b}
            buffetIndex={b.originalIndex}
            flaggedMap={flaggedMap}
            onContextMenuOpen={handleOpenContextMenu}
          />
        ))}

      {/* Side Duty Cards */}
      {(activeFilter === 'ALL' || activeFilter === 'SIDE DUTIES') &&
        filteredData.sideDuties.map((s) => (
          <SideDutyCard
            key={`side-${s.originalIndex}`}
            item={s}
            sideDutyIndex={s.originalIndex}
            flaggedMap={flaggedMap}
            onContextMenuOpen={handleOpenContextMenu}
          />
        ))}

      {/* Special Events */}
      {activeFilter === 'ALL' && filteredData.specialEvents.length > 0 && (
        <SpecialEventsCard
          events={filteredData.specialEvents}
          onContextMenuOpen={handleOpenContextMenu}
        />
      )}

      {/* Sick Leave */}
      {activeFilter === 'ALL' && (
        <SickLeaveCard
          sickList={filteredData.sickLeave || []}
          flaggedMap={flaggedMap}
          onContextMenuOpen={handleOpenContextMenu}
        />
      )}

      {/* Floating Context Menu */}
      <ContextMenu
        menuState={contextMenu}
        onClose={handleCloseContextMenu}
        onSelectAction={handleContextMenuAction}
      />

      {/* Slide-out Edit Drawer / Modal */}
      <SideEditModal
        isOpen={modalState.isOpen}
        mode={modalState.mode}
        target={modalState.target}
        scheduleData={data}
        onClose={() => setModalState((prev) => ({ ...prev, isOpen: false }))}
        onConfirmMove={onMoveCrew}
        onConfirmTiming={onUpdateTiming}
        onConfirmTables={onUpdateTables}
        onConfirmEditCrew={onUpdateCrewDetails}
        onConfirmAddCrew={onAddCrew}
      />
    </div>
  )
}
