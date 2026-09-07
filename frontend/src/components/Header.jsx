import { motion } from 'motion/react'
import { Ship, Calendar, MapPin } from 'lucide-react'

export default function Header({ data }) {
  const { ship = 'COSTA SMERALDA', date = '—', port = '—' } = data || {}

  return (
    <header className="flex items-center justify-between w-full shrink-0 select-none gap-4">
      {/* Title only (no long subtitle) */}
      <h1 className="text-lg font-black text-[var(--text-primary)] tracking-tight leading-none truncate">
        Costa Schedule Exporter
      </h1>

      {/* Right Telemetry Badges — Strictly 1 Single Line */}
      <div className="flex items-center gap-2 shrink-0 flex-nowrap overflow-x-auto">
        {/* Vessel Badge */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
          className="whitespace-nowrap inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[var(--badge-vessel-bg)] border border-[var(--badge-vessel-border)] shadow-xs shrink-0"
        >
          <Ship size={13} className="text-[var(--badge-vessel-text)] shrink-0" />
          <span className="text-xs font-bold text-[var(--badge-vessel-text)]">
            {ship}
          </span>
        </motion.div>

        {/* Date Badge */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2, delay: 0.05 }}
          className="whitespace-nowrap inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#FEF3C7] dark:bg-[#2B1D08] border border-[#FDE68A] dark:border-[#92400E] shadow-xs shrink-0"
        >
          <Calendar size={13} className="text-[#D97706] dark:text-[#F59E0B] shrink-0" />
          <span className="text-xs font-bold text-[#B45309] dark:text-[#FBBF24]">
            {date}
          </span>
        </motion.div>

        {/* Port Badge */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2, delay: 0.1 }}
          className="whitespace-nowrap inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#E0F2FE] dark:bg-[#092535] border border-[#BAE6FD] dark:border-[#0C4A6E] shadow-xs shrink-0"
        >
          <MapPin size={13} className="text-[#0284C7] dark:text-[#38BDF8] shrink-0" />
          <span className="text-xs font-bold text-[#0369A1] dark:text-[#7DD3FC]">
            {port}
          </span>
        </motion.div>
      </div>
    </header>
  )
}
