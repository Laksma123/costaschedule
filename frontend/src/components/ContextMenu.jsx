import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  ArrowRightLeft,
  Clock,
  Armchair,
  Edit3,
  UserPlus,
  Trash2,
  HeartPulse,
} from 'lucide-react'

export default function ContextMenu({ menuState, onClose, onSelectAction }) {
  const menuRef = useRef(null)

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        onClose()
      }
    }

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }

    window.addEventListener('mousedown', handleOutsideClick)
    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('mousedown', handleOutsideClick)
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [onClose])

  if (!menuState || !menuState.isOpen) return null

  const { x, y, targetType, title, subtitle, canChangeTiming, canEditTables, canMove, isSickLeave } = menuState

  // Ensure menu doesn't clip past screen boundary
  const menuWidth = 220
  const menuHeight = 240
  const adjustedX = Math.max(10, Math.min(x, window.innerWidth - menuWidth - 10))
  const adjustedY = Math.max(10, Math.min(y, window.innerHeight - menuHeight - 10))

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 pointer-events-none">
        <motion.div
          ref={menuRef}
          initial={{ opacity: 0, scale: 0.94, y: -4 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.94, y: -4 }}
          transition={{ duration: 0.12, ease: 'easeOut' }}
          style={{ left: adjustedX, top: adjustedY }}
          className="pointer-events-auto absolute w-56 rounded-xl bg-[var(--surface-card)] border border-[var(--border-card)] shadow-2xl overflow-hidden py-1.5 backdrop-blur-md"
        >
          {/* Header Preview */}
          <div className="px-3 py-2 border-b border-[var(--border-subtle)] bg-[var(--surface-inner)]/80">
            <div className="text-[11px] font-bold text-[var(--text-primary)] truncate">
              {title || 'Actions'}
            </div>
            {subtitle && (
              <div className="text-[10px] text-[var(--text-subtle)] truncate mt-0.5">
                {subtitle}
              </div>
            )}
          </div>

          <div className="py-1">
            {/* 1. Move To Action */}
            {canMove !== false && (
              <button
                onClick={() => onSelectAction('move')}
                className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] hover:text-[var(--accent-color)] transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2.5">
                  <ArrowRightLeft size={14} className="text-[var(--accent-color)]" />
                  <span>Move To...</span>
                </div>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[var(--accent-dim)] text-[var(--accent-text)]">
                  Side Modal ›
                </span>
              </button>
            )}

            {/* Move to Sick Leave Shortcut */}
            {!isSickLeave && targetType !== 'section_header' && (
              <button
                onClick={() => onSelectAction('move_to_sick')}
                className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs text-[#E11D48] dark:text-[#FB7185] hover:bg-[#FFE4E6]/50 dark:hover:bg-[#2E0E15]/50 transition-colors cursor-pointer"
              >
                <HeartPulse size={14} />
                <span>Move to Sick Leave</span>
              </button>
            )}

            {/* 2. Change Timing Action */}
            {canChangeTiming && (
              <button
                onClick={() => onSelectAction('timing')}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] hover:text-[var(--accent-color)] transition-colors cursor-pointer"
              >
                <Clock size={14} className="text-[#D97706] dark:text-[#F59E0B]" />
                <span>Change Timing</span>
              </button>
            )}

            {/* 3. Edit Tables Action */}
            {canEditTables && (
              <button
                onClick={() => onSelectAction('tables')}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] hover:text-[var(--accent-color)] transition-colors cursor-pointer"
              >
                <Armchair size={14} className="text-[#0284C7] dark:text-[#38BDF8]" />
                <span>Edit Tables</span>
              </button>
            )}

            {/* 4. Edit Crew Details */}
            {targetType !== 'section_header' && (
              <button
                onClick={() => onSelectAction('edit_crew')}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-colors cursor-pointer"
              >
                <Edit3 size={14} className="text-[var(--text-subtle)]" />
                <span>Edit Details</span>
              </button>
            )}

            {/* 5. Add Personnel (for Section Headers) */}
            {targetType === 'section_header' && (
              <button
                onClick={() => onSelectAction('add_crew')}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] hover:text-[var(--accent-color)] transition-colors cursor-pointer"
              >
                <UserPlus size={14} className="text-[#059669] dark:text-[#10B981]" />
                <span>Add Personnel</span>
              </button>
            )}

            {/* Divider */}
            <div className="h-px bg-[var(--border-subtle)] my-1" />

            {/* 6. Remove Action */}
            {targetType !== 'section_header' && (
              <button
                onClick={() => onSelectAction('delete')}
                className="w-full flex items-center gap-2.5 px-3 py-1.5 text-xs text-[#DC2626] dark:text-[#F87171] hover:bg-[#FEE2E2]/60 dark:hover:bg-[#450A0A]/40 transition-colors cursor-pointer"
              >
                <Trash2 size={13} />
                <span>Remove</span>
              </button>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
