import { motion, AnimatePresence } from 'motion/react'
import { ClipboardCopy, CheckCircle2, Globe, Save, FolderCheck } from 'lucide-react'

export default function ActionBar({
  onCopy,
  onOpenWebapp,
  onSaveBackup,
  copyState = 'idle',
  saveState = 'idle',
  lastSavedFile = '',
}) {
  const isCopied = copyState === 'copied'
  const isSaved = saveState === 'saved'

  return (
    <footer className="w-full flex items-center gap-3 shrink-0 select-none">
      {/* Primary CTA: Copy Encrypted Payload */}
      <motion.button
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.98 }}
        onClick={onCopy}
        className={`flex-1 flex items-center justify-center gap-2.5 py-3 px-6 rounded-xl text-sm font-bold text-white shadow-md transition-all duration-200 cursor-pointer overflow-hidden relative ${
          isCopied
            ? 'bg-[#059669] hover:bg-[#047857] shadow-[#059669]/20'
            : 'bg-[var(--accent-color)] hover:bg-[var(--accent-hover)] shadow-[var(--accent-color)]/25'
        }`}
      >
        <AnimatePresence mode="wait" initial={false}>
          {isCopied ? (
            <motion.div
              key="copied"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
              className="flex items-center gap-2"
            >
              <CheckCircle2 size={16} />
              <span>✓ COPIED TO CLIPBOARD! READY TO PASTE ON WHATSAPP</span>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.15 }}
              className="flex items-center gap-2"
            >
              <ClipboardCopy size={16} />
              <span>COPY ENCRYPTED SCHEDULE TO CLIPBOARD</span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Save Data JSON Backup Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onSaveBackup}
        className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl border text-xs font-bold shadow-xs transition-all duration-150 shrink-0 cursor-pointer ${
          isSaved
            ? 'bg-[#D1FAE5] dark:bg-[#06281D] text-[#059669] dark:text-[#10B981] border-[#A7F3D0] dark:border-[#047857]'
            : 'bg-[var(--surface-card)] border-[var(--border-subtle)] hover:border-[#10B981] text-[var(--text-primary)] hover:text-[#059669] dark:hover:text-[#10B981]'
        }`}
        title={lastSavedFile ? `Last saved: ${lastSavedFile}` : 'Save JSON backup to Save Data folder with timestamp'}
      >
        <AnimatePresence mode="wait" initial={false}>
          {isSaved ? (
            <motion.div
              key="saved"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex items-center gap-1.5"
            >
              <FolderCheck size={15} className="text-[#059669] dark:text-[#10B981]" />
              <span>✓ Saved to Save Data!</span>
            </motion.div>
          ) : (
            <motion.div
              key="idle-save"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex items-center gap-1.5"
            >
              <Save size={15} className="text-[#059669] dark:text-[#10B981]" />
              <span>Save to Save Data</span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Secondary Button: Open WebApp Viewer */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onOpenWebapp}
        className="flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-[var(--surface-card)] border border-[var(--border-subtle)] hover:border-[var(--accent-border)] text-xs font-bold text-[var(--text-primary)] shadow-xs transition-all duration-150 shrink-0 cursor-pointer"
      >
        <Globe size={15} className="text-[var(--accent-color)]" />
        <span>Open WebApp Viewer</span>
      </motion.button>
    </footer>
  )
}
