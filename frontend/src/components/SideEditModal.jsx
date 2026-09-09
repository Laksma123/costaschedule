import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  X,
  ArrowRightLeft,
  Clock,
  Armchair,
  Edit3,
  UserPlus,
  CheckCircle2,
  AlertCircle,
  Building2,
  Salad,
  Zap,
  HeartPulse,
  User,
  Users,
  Plus,
} from 'lucide-react'
import { extractAllSections } from '../utils/rosterUtils'

export default function SideEditModal({
  isOpen,
  mode,
  target,
  scheduleData,
  onClose,
  onConfirmMove,
  onConfirmTiming,
  onConfirmTables,
  onConfirmEditCrew,
  onConfirmAddCrew,
}) {
  const sections = useMemo(() => extractAllSections(scheduleData), [scheduleData])

  // Move Form State
  const [selectedSectionId, setSelectedSectionId] = useState('')
  const [selectedStationIndex, setSelectedStationIndex] = useState('new')
  const [selectedRole, setSelectedRole] = useState('waiter')
  const [customRole, setCustomRole] = useState('')

  // Timing Form State
  const [timingVal, setTimingVal] = useState('')

  // Tables Form State
  const [tablesVal, setTablesVal] = useState('')

  // Crew Form State (Edit / Add)
  const [crewName, setCrewName] = useState('')
  const [crewRole, setCrewRole] = useState('')
  const [stationName, setStationName] = useState('')

  // Initialize values when target/mode changes
  useEffect(() => {
    if (!isOpen || !target) return

    if (mode === 'move') {
      if (sections.length > 0) {
        // Default to first section that isn't current, or first available
        const defaultSec = sections.find(s => s.id !== target.sourceSectionId) || sections[0]
        setSelectedSectionId(defaultSec?.id || '')
        setSelectedStationIndex('new')
        setSelectedRole('waiter')
        setCustomRole(target.crew?.role || '')
      }
    } else if (mode === 'timing') {
      setTimingVal(target.currentTiming || '')
    } else if (mode === 'tables') {
      setTablesVal(target.currentTables || '')
    } else if (mode === 'edit_crew') {
      setCrewName(target.crew?.name || '')
      setCrewRole(target.crew?.role || '')
    } else if (mode === 'add_crew') {
      setCrewName('')
      setCrewRole('')
      setStationName('')
      setTablesVal('')
    }
  }, [isOpen, mode, target, sections])

  if (!isOpen || !target) return null

  const activeSelectedSection = sections.find(s => s.id === selectedSectionId)

  // Handlers
  const handleSaveMove = (e) => {
    e.preventDefault()
    if (!activeSelectedSection) return

    const targetPayload = {
      type: activeSelectedSection.type,
      venueIndex: activeSelectedSection.venueIndex,
      buffetIndex: activeSelectedSection.buffetIndex,
      sideDutyIndex: activeSelectedSection.sideDutyIndex,
      role: activeSelectedSection.type === 'buffet' ? customRole : selectedRole,
    }

    if (activeSelectedSection.type === 'venue') {
      if (selectedStationIndex !== 'new') {
        targetPayload.assignmentIndex = parseInt(selectedStationIndex, 10)
      } else {
        targetPayload.stationName = stationName || `Station ${(activeSelectedSection.stations || []).length + 1}`
      }
    }

    onConfirmMove(target.sourceLocation, targetPayload, target.crew)
    onClose()
  }

  const handleSaveTiming = (e) => {
    e.preventDefault()
    if (!timingVal.trim()) return
    onConfirmTiming(target.targetLocation, timingVal.trim())
    onClose()
  }

  const handleSaveTables = (e) => {
    e.preventDefault()
    onConfirmTables(target.venueIndex, target.assignmentIndex, tablesVal.trim())
    onClose()
  }

  const handleSaveEditCrew = (e) => {
    e.preventDefault()
    if (!crewName.trim()) return
    onConfirmEditCrew(target.location, {
      name: crewName.trim(),
      role: crewRole.trim(),
    })
    onClose()
  }

  const handleSaveAddCrew = (e) => {
    e.preventDefault()
    if (!crewName.trim()) return
    onConfirmAddCrew(target.targetSection, {
      name: crewName.trim(),
      role: crewRole.trim() || selectedRole,
      station: stationName.trim(),
      tables: tablesVal.trim(),
    })
    onClose()
  }

  const timingPresets = [
    '10:45',
    '11:00',
    '11:15-14:15',
    '11:30',
    '07:00-10:00 / 11:00-14:00',
    '08:00-14:00',
    '12:30-15:30/16:30-24:30',
    '13:00',
    'Shift Duty',
  ]

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/50 backdrop-blur-xs cursor-pointer"
        />

        {/* Slide-out Drawer */}
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 30, stiffness: 300 }}
          className="relative w-full max-w-md h-full bg-[var(--surface-card)] border-l border-[var(--border-card)] shadow-2xl flex flex-col z-10 overflow-hidden"
        >
          {/* Top Modal Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-subtle)] bg-[var(--surface-inner)]/60">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-[var(--accent-dim)] text-[var(--accent-text)]">
                {mode === 'move' && <ArrowRightLeft size={16} />}
                {mode === 'timing' && <Clock size={16} />}
                {mode === 'tables' && <Armchair size={16} />}
                {mode === 'edit_crew' && <Edit3 size={16} />}
                {mode === 'add_crew' && <UserPlus size={16} />}
              </div>
              <div>
                <h2 className="text-sm font-bold text-[var(--text-primary)]">
                  {mode === 'move' && 'Move Crew Member'}
                  {mode === 'timing' && 'Change Timing'}
                  {mode === 'tables' && 'Edit Table Assignment'}
                  {mode === 'edit_crew' && 'Edit Personnel Details'}
                  {mode === 'add_crew' && 'Add Crew Member'}
                </h2>
                <p className="text-[11px] text-[var(--text-subtle)]">
                  {mode === 'move' && 'Transfer personnel to another active outlet or duty section'}
                  {mode === 'timing' && 'Update report hour or operational timing schedule'}
                  {mode === 'tables' && 'Modify dining station table allocation numbers'}
                  {mode === 'edit_crew' && 'Update name spelling or duty role'}
                  {mode === 'add_crew' && `Append crew to ${target.sectionName || 'active section'}`}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[var(--text-subtle)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-colors cursor-pointer"
            >
              <X size={16} />
            </button>
          </div>

          {/* Modal Body Container */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {/* ════════════ MODE 1: MOVE CREW ════════════ */}
            {mode === 'move' && (
              <form onSubmit={handleSaveMove} className="space-y-4">
                {/* Active Crew Summary Box */}
                <div className="p-3.5 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] space-y-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-subtle)]">
                    Selected Crew to Move
                  </span>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-[var(--surface-badge)] border border-[var(--border-card)] flex items-center justify-center shrink-0">
                        <User size={13} className="text-[#0071A3]" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-[var(--text-primary)]">
                          {target.crew?.name || 'Unknown'}
                        </div>
                        {target.crew?.role && (
                          <div className="text-[10px] text-[var(--accent-text)] font-semibold">
                            Role: {target.crew.role}
                          </div>
                        )}
                      </div>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-[var(--surface-badge)] border border-[var(--border-card)] text-[var(--text-secondary)] font-medium">
                      From: {target.sourceSectionName || 'Current Duty'}
                    </span>
                  </div>
                </div>

                {/* Destination Dropdown */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[var(--text-primary)] flex items-center justify-between">
                    <span>Destination Outlet / Category</span>
                    <span className="text-[10px] text-[var(--accent-text)] font-semibold">
                      {sections.length} active detected
                    </span>
                  </label>
                  <select
                    value={selectedSectionId}
                    onChange={(e) => setSelectedSectionId(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-color)] focus:ring-1 focus:ring-[var(--accent-color)] transition-all cursor-pointer font-medium"
                  >
                    {['Main Dining Restaurants', 'Buffet & Specialty Outlets', 'Sub-Teams & Side Duties', 'Sick Leave / Off Duty'].map(group => {
                      const groupSections = sections.filter(s => s.group === group)
                      if (groupSections.length === 0) return null
                      return (
                        <optgroup key={group} label={`── ${group} ──`}>
                          {groupSections.map(s => (
                            <option key={s.id} value={s.id}>
                              {s.name}
                            </option>
                          ))}
                        </optgroup>
                      )
                    })}
                  </select>
                </div>

                {/* Destination Specific Inputs */}
                {activeSelectedSection?.type === 'venue' && (
                  <div className="p-3.5 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] space-y-3">
                    <div className="text-[11px] font-bold text-[var(--text-primary)] flex items-center gap-1.5">
                      <Building2 size={13} className="text-[var(--accent-color)]" />
                      <span>Main Dining Configuration</span>
                    </div>

                    <div className="space-y-1">
                      <label className="text-[11px] font-medium text-[var(--text-secondary)]">
                        Target Station
                      </label>
                      <select
                        value={selectedStationIndex}
                        onChange={(e) => setSelectedStationIndex(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg text-xs bg-[var(--surface-card)] border border-[var(--border-subtle)] text-[var(--text-primary)] cursor-pointer"
                      >
                        <option value="new">+ Add New Station Row</option>
                        {(activeSelectedSection.stations || []).map(stn => (
                          <option key={stn.assignmentIndex} value={stn.assignmentIndex}>
                            {stn.station} (Waiter: {stn.waiterName || 'Empty'} | Att: {stn.attendantName || 'Empty'})
                          </option>
                        ))}
                      </select>
                    </div>

                    {selectedStationIndex === 'new' && (
                      <div className="space-y-1">
                        <label className="text-[11px] font-medium text-[var(--text-secondary)]">
                          Station Name / Number
                        </label>
                        <input
                          type="text"
                          value={stationName}
                          onChange={(e) => setStationName(e.target.value)}
                          placeholder={`Station ${(activeSelectedSection.stations || []).length + 1}`}
                          className="w-full px-3 py-2 rounded-lg text-xs bg-[var(--surface-card)] border border-[var(--border-subtle)] text-[var(--text-primary)]"
                        />
                      </div>
                    )}

                    <div className="space-y-1">
                      <label className="text-[11px] font-medium text-[var(--text-secondary)]">
                        Assigned Role
                      </label>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setSelectedRole('waiter')}
                          className={`flex-1 py-1.5 text-xs font-bold rounded-lg border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                            selectedRole === 'waiter'
                              ? 'bg-[#0A2A38] text-white border-[#0A2A38]'
                              : 'bg-[var(--surface-card)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:border-[#CBD5E1]'
                          }`}
                        >
                          <User size={13} />
                          <span>Waiter</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setSelectedRole('attendant')}
                          className={`flex-1 py-1.5 text-xs font-bold rounded-lg border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                            selectedRole === 'attendant'
                              ? 'bg-[#0A2A38] text-white border-[#0A2A38]'
                              : 'bg-[var(--surface-card)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:border-[#CBD5E1]'
                          }`}
                        >
                          <Users size={13} />
                          <span>Attendant</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {activeSelectedSection?.type === 'buffet' && (
                  <div className="p-3.5 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] space-y-2">
                    <div className="text-[11px] font-bold text-[var(--text-primary)] flex items-center gap-1.5">
                      <Salad size={13} className="text-[#10B981]" />
                      <span>Outlet Sub-Role / Duty (Optional)</span>
                    </div>
                    <input
                      type="text"
                      value={customRole}
                      onChange={(e) => setCustomRole(e.target.value)}
                      placeholder="e.g. Pizzeria, Salty Beach, Sushino, Lead..."
                      className="w-full px-3 py-2 rounded-lg text-xs bg-[var(--surface-card)] border border-[var(--border-subtle)] text-[var(--text-primary)]"
                    />
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {['Pizzeria', 'Salty Beach', 'Sushino', 'Hot Pot', 'Buffet Deck 9'].map(sug => (
                        <button
                          type="button"
                          key={sug}
                          onClick={() => setCustomRole(sug)}
                          className="px-2 py-0.5 rounded-md text-[10px] bg-[var(--surface-card)] border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-border)] cursor-pointer"
                        >
                          +{sug}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {activeSelectedSection?.type === 'sickLeave' && (
                  <div className="p-3.5 rounded-xl bg-[#FFE4E6]/60 dark:bg-[#2E0E15]/60 border border-[#FECDD3] dark:border-[#881337] flex items-center gap-3">
                    <HeartPulse size={20} className="text-[#E11D48] dark:text-[#FB7185] shrink-0" />
                    <div className="text-xs text-[#9F1239] dark:text-[#FECDD3]">
                      Crew will be moved to <strong>Sick Leave / Off Duty</strong> and relieved from active dining floor stations.
                    </div>
                  </div>
                )}

                <div className="pt-2">
                  <button
                    type="submit"
                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[var(--accent-color)] hover:bg-[var(--accent-hover)] shadow-md transition-all cursor-pointer"
                  >
                    <CheckCircle2 size={15} />
                    <span>Confirm & Move Personnel</span>
                  </button>
                </div>
              </form>
            )}

            {/* ════════════ MODE 2: CHANGE TIMING ════════════ */}
            {mode === 'timing' && (
              <form onSubmit={handleSaveTiming} className="space-y-4">
                <div className="p-3.5 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] space-y-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-subtle)]">
                    Target
                  </span>
                  <div className="text-xs font-bold text-[var(--text-primary)]">
                    {target.targetName || 'Selected Section'}
                  </div>
                  <div className="text-[11px] text-[var(--text-secondary)]">
                    Current: <span className="font-mono font-bold text-[var(--accent-text)]">{target.currentTiming || '—'}</span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[var(--text-primary)]">
                    New Timing Value
                  </label>
                  <input
                    type="text"
                    value={timingVal}
                    onChange={(e) => setTimingVal(e.target.value)}
                    placeholder="e.g. 11:00 or 07:00-10:00 / 11:00-14:00"
                    className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-color)] font-mono font-semibold"
                  />
                </div>

                {/* Quick Presets */}
                <div className="space-y-1.5">
                  <label className="text-[11px] font-bold text-[var(--text-subtle)]">
                    Quick Presets
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {timingPresets.map(preset => (
                      <button
                        type="button"
                        key={preset}
                        onClick={() => setTimingVal(preset)}
                        className="px-2.5 py-1 rounded-lg text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] hover:border-[var(--accent-border)] text-[var(--text-primary)] font-mono cursor-pointer transition-colors"
                      >
                        {preset}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[var(--accent-color)] hover:bg-[var(--accent-hover)] shadow-md transition-all cursor-pointer"
                  >
                    <CheckCircle2 size={15} />
                    <span>Save Timing</span>
                  </button>
                </div>
              </form>
            )}

            {/* ════════════ MODE 3: EDIT TABLES ════════════ */}
            {mode === 'tables' && (
              <form onSubmit={handleSaveTables} className="space-y-4">
                <div className="p-3.5 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-subtle)]">
                    Dining Station
                  </span>
                  <div className="text-xs font-bold text-[var(--text-primary)]">
                    {target.stationName || 'Station'} — {target.venueName || 'Main Dining'}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[var(--text-primary)]">
                    Table Allocation Numbers
                  </label>
                  <input
                    type="text"
                    value={tablesVal}
                    onChange={(e) => setTablesVal(e.target.value)}
                    placeholder="e.g. 51-54, 55, 56"
                    className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-color)] font-mono font-semibold"
                  />
                  <p className="text-[10px] text-[var(--text-subtle)]">
                    Enter table numbers or ranges. Leave empty to remove tables assignment.
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setTablesVal('')}
                    className="px-3 py-1.5 rounded-lg text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] cursor-pointer"
                  >
                    Clear Tables
                  </button>
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[var(--accent-color)] hover:bg-[var(--accent-hover)] shadow-md transition-all cursor-pointer"
                  >
                    <CheckCircle2 size={15} />
                    <span>Save Table Allocation</span>
                  </button>
                </div>
              </form>
            )}

            {/* ════════════ MODE 4: EDIT CREW DETAILS ════════════ */}
            {mode === 'edit_crew' && (
              <form onSubmit={handleSaveEditCrew} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[var(--text-primary)]">
                    Full Name (as on Roster)
                  </label>
                  <input
                    type="text"
                    value={crewName}
                    onChange={(e) => setCrewName(e.target.value)}
                    placeholder="e.g. SEMERTI NI MADE DIAN BUDI"
                    className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-color)] font-semibold"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[var(--text-primary)]">
                    Duty Role / Note (Optional)
                  </label>
                  <input
                    type="text"
                    value={crewRole}
                    onChange={(e) => setCrewRole(e.target.value)}
                    placeholder="e.g. Pizzeria, Lead, Hot Pot Team..."
                    className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-color)]"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[var(--accent-color)] hover:bg-[var(--accent-hover)] shadow-md transition-all cursor-pointer"
                  >
                    <CheckCircle2 size={15} />
                    <span>Save Personnel Changes</span>
                  </button>
                </div>
              </form>
            )}

            {/* ════════════ MODE 5: ADD CREW ════════════ */}
            {mode === 'add_crew' && (
              <form onSubmit={handleSaveAddCrew} className="space-y-4">
                <div className="p-3.5 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-subtle)]">
                    Target Duty Section
                  </span>
                  <div className="text-xs font-bold text-[var(--text-primary)]">
                    {target.sectionName || 'Duty Section'}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[var(--text-primary)]">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    value={crewName}
                    onChange={(e) => setCrewName(e.target.value)}
                    placeholder="e.g. JOHN DOE"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-color)] font-semibold"
                  />
                </div>

                {target.targetSection?.type === 'venue' && (
                  <>
                    <div className="space-y-1.5">
                      <label className="text-xs font-bold text-[var(--text-primary)]">
                        Station Name
                      </label>
                      <input
                        type="text"
                        value={stationName}
                        onChange={(e) => setStationName(e.target.value)}
                        placeholder="e.g. Stn 15"
                        className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] font-mono"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-bold text-[var(--text-primary)]">
                        Assigned Role
                      </label>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setSelectedRole('waiter')}
                          className={`flex-1 py-1.5 text-xs font-bold rounded-lg border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                            selectedRole === 'waiter'
                              ? 'bg-[#0A2A38] text-white border-[#0A2A38]'
                              : 'bg-[var(--surface-card)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:border-[#CBD5E1]'
                          }`}
                        >
                          <User size={13} />
                          <span>Waiter</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => setSelectedRole('attendant')}
                          className={`flex-1 py-1.5 text-xs font-bold rounded-lg border transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                            selectedRole === 'attendant'
                              ? 'bg-[#0A2A38] text-white border-[#0A2A38]'
                              : 'bg-[var(--surface-card)] text-[var(--text-secondary)] border-[var(--border-subtle)] hover:border-[#CBD5E1]'
                          }`}
                        >
                          <Users size={13} />
                          <span>Attendant</span>
                        </button>
                      </div>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-xs font-bold text-[var(--text-primary)]">
                        Table Numbers
                      </label>
                      <input
                        type="text"
                        value={tablesVal}
                        onChange={(e) => setTablesVal(e.target.value)}
                        placeholder="e.g. 81-84"
                        className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] font-mono"
                      />
                    </div>
                  </>
                )}

                {target.targetSection?.type === 'buffet' && (
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-[var(--text-primary)]">
                      Outlet Role (Optional)
                    </label>
                    <input
                      type="text"
                      value={crewRole}
                      onChange={(e) => setCrewRole(e.target.value)}
                      placeholder="e.g. Pizzeria, Noodle Bar"
                      className="w-full px-3.5 py-2.5 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)]"
                    />
                  </div>
                )}

                <div className="pt-2">
                  <button
                    type="submit"
                    className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-[var(--accent-color)] hover:bg-[var(--accent-hover)] shadow-md transition-all cursor-pointer"
                  >
                    <UserPlus size={15} />
                    <span>Add Personnel to Roster</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
