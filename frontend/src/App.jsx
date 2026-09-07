import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { FileSpreadsheet, UploadCloud } from 'lucide-react'
import { usePyBridge } from './hooks/usePyBridge'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import ControlCard from './components/ControlCard'
import TabView from './components/TabView'
import BentoExplorer from './components/BentoExplorer'
import PayloadTab from './components/PayloadTab'
import OverviewTab from './components/OverviewTab'
import ActionBar from './components/ActionBar'
import {
  moveCrew,
  updateTiming,
  updateTables,
  updateCrewDetails,
  addCrewToSection,
  deleteCrewFromSection,
  generateWhatsAppPayload,
  calculateTelemetry,
  detectDuplicates,
} from './utils/rosterUtils'

export default function App() {
  const { isReady, api } = usePyBridge()

  // ── Theme State: 'dark' | 'light' | 'sakura' ──
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('costa_theme') || 'sakura'
  })

  useEffect(() => {
    document.documentElement.classList.remove('dark', 'sakura')
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else if (theme === 'sakura') {
      document.documentElement.classList.add('sakura')
    }
    localStorage.setItem('costa_theme', theme)
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme(prev => {
      if (prev === 'dark') return 'light'
      if (prev === 'light') return 'sakura'
      return 'dark'
    })
  }, [])

  const setThemeExplicit = useCallback((mode) => {
    setTheme(mode)
  }, [])

  // ── Schedule State ──
  const [scheduleData, setScheduleData] = useState(null)
  const [fileName, setFileName] = useState('')
  const [filePath, setFilePath] = useState('')
  const [payload, setPayload] = useState('')
  const [telemetry, setTelemetry] = useState({})
  const [isProcessing, setIsProcessing] = useState(false)

  // ── UI State ──
  const [mealShift, setMealShift] = useState('LUNCH')
  const [activeTab, setActiveTab] = useState('bento')
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFilter, setActiveFilter] = useState('ALL')
  const [copyState, setCopyState] = useState('idle') // idle | copied
  const [saveState, setSaveState] = useState('idle') // idle | saved
  const [lastSavedFile, setLastSavedFile] = useState('')
  const [targetCrewCount, setTargetCrewCount] = useState(() => {
    return localStorage.getItem('costa_target_crew') || ''
  })

  const handleTargetCrewChange = useCallback((val) => {
    setTargetCrewCount(val)
    if (val) {
      localStorage.setItem('costa_target_crew', val)
    } else {
      localStorage.removeItem('costa_target_crew')
    }
  }, [])

  // ── Auto-load on bridge ready ──
  useEffect(() => {
    if (!isReady || !api) return
    loadInitialData()
  }, [isReady, api])

  const loadInitialData = async () => {
    if (!api) return
    setIsProcessing(true)
    try {
      const result = await api.get_initial_data()
      if (result.status === 'ok') {
        applyResult(result)
      }
    } catch (err) {
      console.error('Failed to load initial data:', err)
    }
    setIsProcessing(false)
  }

  const applyResult = (result) => {
    setScheduleData(result.data)
    setFileName(result.file || '')
    setFilePath(result.filePath || '')
    setPayload(result.payload || '')
    setTelemetry(result.telemetry || {})
  }

  // ── Core Schedule State Mutation & Live Sync ──
  const handleScheduleMutation = useCallback((newScheduleData) => {
    setScheduleData(newScheduleData)

    const { payload: newPayload, b64: newB64 } = generateWhatsAppPayload(newScheduleData)
    setPayload(newPayload)

    const newTelemetry = calculateTelemetry(newScheduleData, newPayload, newB64)
    setTelemetry(newTelemetry)

    // Sync to Python backend bridge in background
    if (api && api.update_schedule_data) {
      api.update_schedule_data(newScheduleData).catch(err => {
        console.warn('Backend sync failed:', err)
      })
    }
  }, [api])

  // ── Edit Handlers for Bento Explorer ──
  const handleMoveCrew = useCallback((sourceLocation, targetLocation, crew) => {
    if (!scheduleData) return
    const updated = moveCrew(scheduleData, sourceLocation, targetLocation, crew)
    handleScheduleMutation(updated)
  }, [scheduleData, handleScheduleMutation])

  const handleUpdateTiming = useCallback((targetLocation, newTiming) => {
    if (!scheduleData) return
    const updated = updateTiming(scheduleData, targetLocation, newTiming)
    handleScheduleMutation(updated)
  }, [scheduleData, handleScheduleMutation])

  const handleUpdateTables = useCallback((venueIndex, assignmentIndex, newTables) => {
    if (!scheduleData) return
    const updated = updateTables(scheduleData, venueIndex, assignmentIndex, newTables)
    handleScheduleMutation(updated)
  }, [scheduleData, handleScheduleMutation])

  const handleUpdateCrewDetails = useCallback((location, updatedCrew) => {
    if (!scheduleData) return
    const updated = updateCrewDetails(scheduleData, location, updatedCrew)
    handleScheduleMutation(updated)
  }, [scheduleData, handleScheduleMutation])

  const handleAddCrew = useCallback((targetSection, newCrew) => {
    if (!scheduleData) return
    const updated = addCrewToSection(scheduleData, targetSection, newCrew)
    handleScheduleMutation(updated)
  }, [scheduleData, handleScheduleMutation])

  const handleDeleteCrew = useCallback((location) => {
    if (!scheduleData) return
    const updated = deleteCrewFromSection(scheduleData, location)
    handleScheduleMutation(updated)
  }, [scheduleData, handleScheduleMutation])

  // ── Native File Operations ──
  const handleBrowse = async () => {
    if (!api) return
    const result = await api.browse_file()
    if (result.status === 'ok') {
      setIsProcessing(true)
      const parsed = await api.parse_schedule(result.file, mealShift)
      if (parsed.status === 'ok') applyResult(parsed)
      setIsProcessing(false)
    }
  }

  const handleReload = async () => {
    if (!api || !filePath) return
    setIsProcessing(true)
    const result = await api.parse_schedule(filePath, mealShift)
    if (result.status === 'ok') applyResult(result)
    setIsProcessing(false)
  }

  const handleShiftChange = async (shift) => {
    setMealShift(shift)
    if (!api || !filePath) return
    setIsProcessing(true)
    const result = await api.parse_schedule(filePath, shift)
    if (result.status === 'ok') applyResult(result)
    setIsProcessing(false)
  }

  const handleCopyPayload = async () => {
    if (!payload) return

    // Write to clipboard in frontend
    try {
      await navigator.clipboard.writeText(payload)
      setCopyState('copied')
      setTimeout(() => setCopyState('idle'), 2400)
    } catch (e) {
      console.warn('Frontend clipboard write failed, using backend bridge:', e)
    }

    // Also notify Python backend to copy to OS clipboard
    if (api) {
      const result = await api.copy_payload()
      if (result.status === 'ok' || result.status === 'fallback') {
        setCopyState('copied')
        setTimeout(() => setCopyState('idle'), 2400)
      }
    }
  }

  const handleCopyText = async (text) => {
    if (!text) return
    try {
      await navigator.clipboard.writeText(text)
    } catch (e) {}
    if (api) {
      await api.copy_text(text)
    }
  }

  const handleSaveJsonBackup = async () => {
    if (!scheduleData) return

    if (api && api.save_json_backup) {
      try {
        const res = await api.save_json_backup(scheduleData)
        if (res.status === 'ok') {
          setLastSavedFile(res.filename)
          setSaveState('saved')
          setTimeout(() => setSaveState('idle'), 2500)
          return
        }
      } catch (err) {
        console.error('Backend save backup failed:', err)
      }
    }

    // Fallback in browser / dev mode: trigger JSON download
    try {
      const now = new Date()
      const timeStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}-${String(now.getMinutes()).padStart(2, '0')}-${String(now.getSeconds()).padStart(2, '0')}`
      const filename = `Costa_Schedule_${timeStr}.json`
      const blob = new Blob([JSON.stringify(scheduleData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setLastSavedFile(filename)
      setSaveState('saved')
      setTimeout(() => setSaveState('idle'), 2500)
    } catch (err) {
      console.error('Fallback save failed:', err)
    }
  }

  const handleExportJson = async () => {
    if (!api) return
    await api.export_json()
  }

  const handleOpenWebapp = async () => {
    if (!api) return
    await api.open_webapp()
  }

  const duplicateReport = useMemo(() => detectDuplicates(scheduleData), [scheduleData])

  // ── Drag & Drop State & Handlers ──
  const [isDraggingFile, setIsDraggingFile] = useState(false)
  const dragCounter = useRef(0)

  const processDroppedFile = useCallback(async (file) => {
    if (!file) return
    const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
    if (!isExcel) {
      alert('Please drop a valid Excel roster file (.xlsx or .xls)')
      return
    }

    setIsProcessing(true)
    try {
      const reader = new FileReader()
      reader.onload = async (e) => {
        const b64Data = e.target.result // Data URL: "data:application/...;base64,..."
        if (api && api.parse_schedule_from_base64) {
          const parsed = await api.parse_schedule_from_base64(b64Data, file.name, mealShift)
          if (parsed.status === 'ok') {
            applyResult(parsed)
          } else {
            alert(`Failed to parse file: ${parsed.message || 'Unknown error'}`)
          }
        }
        setIsProcessing(false)
      }
      reader.onerror = (err) => {
        console.error('File reading failed:', err)
        setIsProcessing(false)
      }
      reader.readAsDataURL(file)
    } catch (err) {
      console.error('Drop error:', err)
      setIsProcessing(false)
    }
  }, [api, mealShift])

  const handleDragEnter = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current += 1
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDraggingFile(true)
    }
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current -= 1
    if (dragCounter.current <= 0) {
      dragCounter.current = 0
      setIsDraggingFile(false)
    }
  }, [])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDraggingFile(false)
    dragCounter.current = 0

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]
      processDroppedFile(file)
    }
  }, [processDroppedFile])

  // ── Render ──
  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className="h-screen flex overflow-hidden bg-[var(--bg-app)] text-[var(--text-primary)] transition-colors duration-200 relative"
    >
      {/* Fullscreen Drag & Drop Dropzone Overlay */}
      <AnimatePresence>
        {isDraggingFile && (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-8 bg-black/65 backdrop-blur-md pointer-events-none"
          >
            <div className="flex flex-col items-center justify-center gap-4 w-full max-w-xl p-10 rounded-3xl border-3 border-dashed border-[var(--accent-color)] bg-[var(--surface-card)]/90 shadow-2xl text-center">
              <motion.div
                animate={{ y: [-6, 6, -6] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                className="p-5 rounded-3xl bg-[var(--accent-dim)] text-[var(--accent-text)] border border-[var(--accent-border)] shadow-lg"
              >
                <UploadCloud size={48} className="animate-pulse text-[var(--accent-color)]" />
              </motion.div>
              <div className="space-y-1">
                <h2 className="text-xl font-black text-[var(--text-primary)]">
                  Drop Costa Schedule (.xlsx) Here
                </h2>
                <p className="text-xs font-semibold text-[var(--text-secondary)]">
                  Release file to instantly parse roster and generate live encrypted payloads
                </p>
              </div>
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[11px] font-bold text-[var(--accent-text)]">
                <FileSpreadsheet size={14} />
                <span>Supports .xlsx & .xls Excel files</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {/* Sidebar */}
      <Sidebar
        telemetry={telemetry}
        theme={theme}
        onThemeToggle={toggleTheme}
        onSetTheme={setThemeExplicit}
        onBrowse={handleBrowse}
        onReload={handleReload}
        isProcessing={isProcessing}
        targetCrewCount={targetCrewCount}
        onTargetCrewChange={handleTargetCrewChange}
        duplicateReport={duplicateReport}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-0 px-5 py-4 gap-3 overflow-hidden">
        <Header data={scheduleData} />

        <ControlCard
          fileName={fileName}
          filePath={filePath}
          mealShift={mealShift}
          onShiftChange={handleShiftChange}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
          onBrowse={handleBrowse}
        />

        <TabView activeTab={activeTab} onTabChange={setActiveTab}>
          {activeTab === 'bento' && (
            <BentoExplorer
              data={scheduleData}
              telemetry={telemetry}
              searchQuery={searchQuery}
              activeFilter={activeFilter}
              payload={payload}
              targetCrewCount={targetCrewCount}
              theme={theme}
              onMoveCrew={handleMoveCrew}
              onUpdateTiming={handleUpdateTiming}
              onUpdateTables={handleUpdateTables}
              onUpdateCrewDetails={handleUpdateCrewDetails}
              onAddCrew={handleAddCrew}
              onDeleteCrew={handleDeleteCrew}
            />
          )}
          {activeTab === 'payload' && (
            <PayloadTab
              payload={payload}
              telemetry={telemetry}
              onCopyPayload={handleCopyPayload}
            />
          )}
          {activeTab === 'overview' && (
            <OverviewTab
              data={scheduleData}
              onCopyText={handleCopyText}
              onExportJson={handleExportJson}
              onSaveBackup={handleSaveJsonBackup}
            />
          )}
        </TabView>

        <ActionBar
          onCopy={handleCopyPayload}
          onOpenWebapp={handleOpenWebapp}
          onSaveBackup={handleSaveJsonBackup}
          copyState={copyState}
          saveState={saveState}
          lastSavedFile={lastSavedFile}
        />
      </main>
    </div>
  )
}
