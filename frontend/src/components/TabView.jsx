import { motion, AnimatePresence } from 'motion/react'
import { Sparkles, MessageSquare, BarChart3 } from 'lucide-react'

const tabs = [
  { id: 'bento', label: 'Visual Bento Explorer', icon: Sparkles },
  { id: 'payload', label: 'WhatsApp Payload', icon: MessageSquare },
  { id: 'overview', label: 'Structured Overview', icon: BarChart3 },
]

export default function TabView({ activeTab, onTabChange, children }) {
  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Tab Pills (HTML/APK Outline Pill Style) */}
      <div className="flex items-center justify-center py-1.5">
        <div className="inline-flex items-center gap-2">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`outline-pill-btn flex items-center gap-2 px-5 py-1.5 text-xs font-semibold ${isActive ? 'active' : ''}`}
              >
                <Icon size={13} />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content Box */}
      <div className="flex-1 min-h-0 overflow-hidden rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface-card)] shadow-xs transition-colors duration-200">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="h-full overflow-y-auto"
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
