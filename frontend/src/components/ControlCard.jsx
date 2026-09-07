import { motion } from 'motion/react'
import { FileSpreadsheet, Search, X } from 'lucide-react'

export default function ControlCard({ 
  fileName = '', 
  filePath = '', 
  mealShift = 'LUNCH', 
  onShiftChange, 
  searchQuery = '', 
  onSearchChange, 
  activeFilter = 'ALL', 
  onFilterChange,
  onBrowse
}) {
  const shifts = ['BREAKFAST', 'LUNCH', 'DINNER']
  const filters = ['ALL', 'MAIN DINING', 'BUFFET & OUTLETS', 'SIDE DUTIES']

  return (
    <div className="w-full p-3.5 rounded-2xl bg-[var(--surface-card)] border border-[var(--border-subtle)] shadow-xs flex flex-col gap-3 shrink-0 select-none transition-colors duration-200">
      {/* Row 1: Source Roster File + Meal Shift */}
      <div className="flex items-center justify-between gap-4">
        {/* Left: Source File Box */}
        <div className="flex-1 flex items-center justify-between min-w-0 px-3.5 py-2 rounded-xl bg-[var(--surface-inner)] border border-[var(--border-subtle)]">
          <div className="flex items-center gap-2.5 min-w-0">
            <FileSpreadsheet size={16} className="text-[var(--accent-color)] shrink-0" />
            <div className="flex flex-col min-w-0">
              <span className="text-xs font-bold text-[var(--text-primary)] truncate">
                {fileName || 'No file loaded'}
              </span>
              <span className="text-[10px] text-[var(--text-subtle)] truncate">
                {filePath || "Click 'Browse...' or Drag & Drop roster (.xlsx) here"}
              </span>
            </div>
          </div>
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
            onClick={onBrowse}
            className="ml-3 px-3 py-1 rounded-lg text-xs font-bold bg-[var(--accent-dim)] hover:bg-[var(--accent-color)] hover:text-white text-[var(--accent-text)] border border-[var(--accent-border)] transition-all duration-150 shrink-0 cursor-pointer"
          >
            Browse...
          </motion.button>
        </div>

        {/* Right: Meal Shift Segmented Buttons */}
        <div className="flex items-center gap-1 p-1 rounded-full bg-[var(--surface-inner)] border border-[var(--border-subtle)] shrink-0">
          {shifts.map((shift) => {
            const isActive = mealShift === shift
            return (
              <button
                key={shift}
                onClick={() => onShiftChange && onShiftChange(shift)}
                className={`relative px-4 py-1.5 rounded-full text-xs font-bold transition-colors duration-150 cursor-pointer ${
                  isActive 
                    ? 'text-white' 
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="shiftIndicator"
                    className="absolute inset-0 bg-[var(--accent-color)] rounded-full shadow-xs"
                    transition={{ type: 'spring', stiffness: 450, damping: 32 }}
                  />
                )}
                <span className="relative z-10">{shift}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Row 2: Live Search Bar + Category Filters */}
      <div className="flex items-center justify-between gap-4">
        {/* Left: Search Input */}
        <div className="flex-1 relative">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-subtle)]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
            placeholder="Filter crew name, station, table, or duty..."
            className="w-full pl-9 pr-8 py-2 rounded-xl text-xs bg-[var(--surface-inner)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-subtle)] focus:outline-none focus:border-[var(--accent-color)] focus:ring-1 focus:ring-[var(--accent-color)] transition-all duration-150"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange && onSearchChange('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded-md text-[var(--text-subtle)] hover:text-[var(--text-primary)] cursor-pointer"
            >
              <X size={13} />
            </button>
          )}
        </div>

        {/* Right: Quick Category Filter Pills */}
        <div className="flex items-center gap-1.5 shrink-0">
          {filters.map((filter) => {
            const isActive = activeFilter === filter
            return (
              <motion.button
                key={filter}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onFilterChange && onFilterChange(filter)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all duration-150 cursor-pointer ${
                  isActive
                    ? 'bg-[var(--accent-dim)] text-[var(--accent-text)] border border-[var(--accent-border)] shadow-xs'
                    : 'bg-[var(--surface-inner)] text-[var(--text-secondary)] border border-[var(--border-subtle)] hover:border-[var(--accent-border)]'
                }`}
              >
                {filter}
              </motion.button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
