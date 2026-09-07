import { motion } from 'motion/react'
import {
  FolderOpen,
  RefreshCw,
  Sun,
  Moon,
  Users,
  Building2,
  Zap,
  Flower2,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react'

export default function Sidebar({
  telemetry = {},
  theme,
  onThemeToggle,
  onSetTheme,
  onBrowse,
  onReload,
  isProcessing,
  targetCrewCount = '',
  onTargetCrewChange,
  duplicateReport = { hasDuplicates: false, totalIssues: 0, idDuplicates: [], nameDuplicates: [], fuzzyDuplicates: [] },
}) {
  const currentCrew = telemetry.crewCount || 0
  const targetNum = parseInt(targetCrewCount, 10)
  const hasTarget = !isNaN(targetNum) && targetNum > 0

  const isDeficit = hasTarget && currentCrew < targetNum
  const isSurplus = hasTarget && currentCrew > targetNum
  const isMatch = hasTarget && currentCrew === targetNum

  const deficitCount = isDeficit ? targetNum - currentCrew : 0
  const surplusCount = isSurplus ? currentCrew - targetNum : 0

  // Deficit highlight classes according to active theme
  const getAlertStyles = () => {
    if (isDeficit) {
      if (theme === 'dark') return 'bg-[#2A1504] border-[#B45309] text-[#FBBF24] ring-1 ring-[#F59E0B]/60 animate-pulse'
      if (theme === 'sakura') return 'bg-[#FFE4EE] border-[#F43F5E] text-[#9F1239] ring-1 ring-[#F43F5E]/60 animate-pulse'
      return 'bg-[#FEF3C7] border-[#F59E0B] text-[#B45309] ring-1 ring-[#F59E0B]/60 animate-pulse'
    }
    if (isSurplus) {
      if (theme === 'dark') return 'bg-[#1C1635] border-[#9333EA] text-[#D8B4FE] ring-1 ring-[#A855F7]/60 animate-pulse'
      if (theme === 'sakura') return 'bg-[#F3E8FF] border-[#C084FC] text-[#7E22CE] ring-1 ring-[#A855F7]/60 animate-pulse'
      return 'bg-[#F3E8FF] border-[#A855F7] text-[#6B21A8] ring-1 ring-[#A855F7]/60 animate-pulse'
    }
    if (isMatch) {
      if (theme === 'dark') return 'bg-[#06281D] border-[#059669] text-[#34D399]'
      if (theme === 'sakura') return 'bg-[#ECFDF5] border-[#10B981] text-[#047857]'
      return 'bg-[#D1FAE5] border-[#10B981] text-[#065F46]'
    }
    return 'bg-transparent'
  }

  return (
    <aside className="w-[268px] h-full flex flex-col shrink-0 border-r border-[var(--border-subtle)] bg-[var(--bg-sidebar)] select-none transition-colors duration-200 overflow-hidden">
      {/* Brand Header */}
      <div className="px-5 pt-4 pb-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] p-1 flex items-center justify-center shadow-xs shrink-0 overflow-hidden">
            <img 
              src="./logo.png" 
              alt="Costa Logo" 
              className="w-full h-full object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <div className="flex flex-col min-w-0">
            <span className="font-black text-sm tracking-tight text-[var(--text-primary)]">
              COSTA SCHEDULE
            </span>
            <span className="inline-flex px-2 py-0.5 rounded-full text-[8.5px] font-bold tracking-wider bg-[var(--accent-dim)] text-[var(--accent-text)] border border-[var(--accent-border)] w-max">
              PRECISION ENGINE v2.6
            </span>
          </div>
        </div>
      </div>

      {/* Hairline Divider */}
      <div className="h-px mx-4 bg-[var(--border-subtle)]" />

      {/* Scrollable Middle Content */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3.5">
        {/* Workflow Actions */}
        <div className="space-y-1.5">
          <span className="text-[9.5px] font-bold tracking-widest text-[var(--text-subtle)] block px-1">
            WORKFLOW ACTIONS
          </span>
          <div className="space-y-1.5">
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={onBrowse}
              disabled={isProcessing}
              className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl
                bg-[var(--surface-inner)] border border-[var(--border-subtle)]
                hover:border-[var(--accent-color)]/50
                hover:bg-[var(--surface-card)]
                text-[var(--text-primary)]
                text-xs font-semibold shadow-xs transition-all duration-150 cursor-pointer disabled:opacity-50"
            >
              <FolderOpen size={15} className="text-[var(--accent-color)] shrink-0" />
              <span className="truncate">Browse Roster (.xlsx)</span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={onReload}
              disabled={isProcessing}
              className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl
                bg-[var(--surface-inner)] border border-[var(--border-subtle)]
                hover:border-[var(--accent-color)]/50
                hover:bg-[var(--surface-card)]
                text-[var(--text-secondary)]
                text-xs font-semibold shadow-xs transition-all duration-150 cursor-pointer disabled:opacity-50"
            >
              <RefreshCw size={15} className={`text-[var(--text-subtle)] shrink-0 ${isProcessing ? 'animate-spin' : ''}`} />
              <span className="truncate">Reload Active File</span>
            </motion.button>

            <div className="flex items-center justify-center gap-1.5 py-1 px-2 rounded-lg bg-[var(--surface-inner)] border border-dashed border-[var(--border-subtle)] text-[9.5px] font-semibold text-[var(--text-subtle)]">
              <span>📥 Drag & Drop .xlsx anywhere</span>
            </div>
          </div>
        </div>

        {/* Global Config Input for Target Crew Count (No Placeholder) */}
        <div className="space-y-1">
          <label className="text-[9.5px] font-bold uppercase tracking-wider text-[var(--text-subtle)] block leading-tight px-1">
            Total Restaurant Crew Non Manager :
          </label>
          <div className="relative">
            <input
              type="number"
              min="0"
              value={targetCrewCount}
              onChange={(e) => onTargetCrewChange && onTargetCrewChange(e.target.value)}
              placeholder=""
              className="w-full pl-3 pr-11 py-1.5 rounded-xl text-xs font-mono font-bold bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-color)] focus:ring-1 focus:ring-[var(--accent-color)] transition-all shadow-2xs"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-[var(--text-subtle)]">
              crew
            </span>
          </div>
        </div>

        {/* Duplicate / Typo Detection Alert Box (If Issues Found) */}
        {duplicateReport?.hasDuplicates && (
          <div className="p-2.5 rounded-xl bg-[#FEF2F2] dark:bg-[#2B0E11] border border-[#FCA5A5] dark:border-[#991B1B] text-[#991B1B] dark:text-[#FCA5A5] space-y-1.5 shadow-xs animate-pulse">
            <div className="flex items-center gap-1.5 text-[10.5px] font-extrabold uppercase tracking-wide">
              <AlertCircle size={13} className="shrink-0 text-[#DC2626] dark:text-[#F87171]" />
              <span>{duplicateReport.totalIssues} Duplicate / Typo Issue(s)</span>
            </div>
            <div className="text-[10px] space-y-1 text-left font-medium leading-tight">
              {(duplicateReport.nameDuplicates || []).map((d, i) => (
                <div key={`name-${i}`} className="truncate">
                  • Duplicate Name <strong>{d.cleanName}</strong> ({d.count}x)
                </div>
              ))}
              {(duplicateReport.fuzzyDuplicates || []).map((d, i) => (
                <div key={`fuz-${i}`} className="truncate">
                  • Typo/Similarity: <em>{d.name1}</em> ≈ <em>{d.name2}</em>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Telemetry Summary Card */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between px-1">
            <span className="text-[9.5px] font-bold tracking-widest text-[var(--text-subtle)]">
              TELEMETRY SUMMARY
            </span>
            {isDeficit ? (
              <span className="text-[8.5px] font-extrabold px-1.5 py-0.5 rounded bg-[#FEF3C7] dark:bg-[#2B1708] text-[#B45309] dark:text-[#FBBF24] border border-[#FDE68A] dark:border-[#92400E] flex items-center gap-0.5 animate-pulse">
                <AlertTriangle size={9} />
                <span>-{deficitCount} DEFICIT</span>
              </span>
            ) : isSurplus ? (
              <span className="text-[8.5px] font-extrabold px-1.5 py-0.5 rounded bg-[#F3E8FF] dark:bg-[#230F38] text-[#7E22CE] dark:text-[#D8B4FE] border border-[#DDD6FE] dark:border-[#5B21B6] flex items-center gap-0.5 animate-pulse">
                <AlertTriangle size={9} />
                <span>+{surplusCount} SURPLUS</span>
              </span>
            ) : isMatch ? (
              <span className="text-[8.5px] font-bold px-1.5 py-0.5 rounded bg-[#D1FAE5] dark:bg-[#06281D] text-[#059669] dark:text-[#10B981] flex items-center gap-0.5">
                <CheckCircle2 size={9} />
                <span>MATCH (100%)</span>
              </span>
            ) : null}
          </div>

          <div className="rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)] p-2.5 space-y-2">
            {/* Total Crew Roster */}
            <div
              className={`flex flex-col gap-0.5 p-2 rounded-lg transition-all duration-200 ${getAlertStyles()}`}
            >
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-[11px] font-semibold text-[var(--text-secondary)]">
                  <Users size={13} className="shrink-0" />
                  Total Crew Roster
                </span>
                {isDeficit && (
                  <span className="text-[9.5px] font-extrabold px-1.5 py-0.2 rounded bg-white/40 dark:bg-black/40">
                    ⚠️ {deficitCount} missing
                  </span>
                )}
                {isSurplus && (
                  <span className="text-[9.5px] font-extrabold px-1.5 py-0.2 rounded bg-white/40 dark:bg-black/40">
                    ⚠️ +{surplusCount} extra
                  </span>
                )}
                {isMatch && (
                  <span className="text-[9.5px] font-bold">
                    ✓ Perfect
                  </span>
                )}
              </div>
              <span className="text-xs font-bold font-mono pl-5">
                : {currentCrew} crew {hasTarget ? `(target: ${targetNum})` : ''}
              </span>
            </div>

            {/* Active Venues */}
            <div className="flex flex-col gap-0.5 px-2">
              <span className="flex items-center gap-1.5 text-[11px] font-medium text-[var(--text-secondary)]">
                <Building2 size={13} className="text-[#D97706] dark:text-[#F59E0B] shrink-0" />
                Active Venues
              </span>
              <span className="text-xs font-bold font-mono text-[var(--text-primary)] pl-5">
                : {telemetry.sectionCount || 0} sections
              </span>
            </div>

            {/* Encrypted Stream */}
            <div className="flex flex-col gap-0.5 px-2">
              <span className="flex items-center gap-1.5 text-[11px] font-medium text-[var(--text-secondary)]">
                <Zap size={13} className="text-[#059669] dark:text-[#10B981] shrink-0" />
                Encrypted Stream
              </span>
              <span className="text-xs font-bold font-mono text-[var(--text-primary)] pl-5">
                : {(telemetry.payloadChars || 0).toLocaleString()} chars
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer: Theme Switcher + Status */}
      <div className="px-4 pb-3.5 space-y-2 border-t border-[var(--border-subtle)] pt-2.5">
        {/* Theme Segmented Switcher (Dark, Light, Sakura) */}
        <div className="flex items-center justify-between p-1 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)]">
          <button
            onClick={() => onSetTheme('dark')}
            title="Dark Theme"
            className={`flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              theme === 'dark'
                ? 'bg-[#181822] text-[#EDEDEF] shadow-xs border border-[#2E3466]'
                : 'text-[var(--text-subtle)] hover:text-[var(--text-primary)]'
            }`}
          >
            <Moon size={12} />
            <span>Dark</span>
          </button>

          <button
            onClick={() => onSetTheme('light')}
            title="Light Theme"
            className={`flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              theme === 'light'
                ? 'bg-white text-[#1A1A2E] shadow-xs border border-[#D5D8F2]'
                : 'text-[var(--text-subtle)] hover:text-[var(--text-primary)]'
            }`}
          >
            <Sun size={12} />
            <span>Light</span>
          </button>

          <button
            onClick={() => onSetTheme('sakura')}
            title="Sakura Pink Theme"
            className={`flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer ${
              theme === 'sakura'
                ? 'bg-[#FFE4EE] text-[#B81D52] shadow-xs border border-[#F9B6CE]'
                : 'text-[var(--text-subtle)] hover:text-[var(--text-primary)]'
            }`}
          >
            <Flower2 size={12} />
            <span>Sakura</span>
          </button>
        </div>

        {/* Engine Status */}
        <div className="flex items-center justify-center gap-2 px-3 py-1.5 rounded-xl bg-[var(--status-ready-bg)] border border-[var(--status-ready-border)]">
          <span className="w-2 h-2 rounded-full bg-[var(--status-ready-text)] animate-pulse" />
          <span className="text-[10.5px] font-bold text-[var(--status-ready-text)]">
            Engine Ready (0% CPU)
          </span>
        </div>
      </div>
    </aside>
  )
}
