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
      {/* Primary CTA: Copy Encrypted Payload (One Primary Yellow Button per Screen Rule) */}
      <motion.button
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.98 }}
        onClick={onCopy}
        className={`flex-1 flex items-center justify-center gap-2.5 py-3 px-6 rounded-xl text-sm font-bold shadow-md transition-all duration-200 cursor-pointer overflow-hidden relative ${
          isCopied
            ? 'bg-[#059669] hover:bg-[#047857] text-white shadow-[#059669]/20'
            : 'bg-[#F9B000] hover:brightness-105 text-[#0A2A38] shadow-[0_2px_8px_rgba(249,176,0,0.3)]'
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
              <span>COPIED TO CLIPBOARD! READY TO PASTE ON WHATSAPP</span>
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
            : 'bg-white dark:bg-[var(--surface-card)] border-[#CBD5E1] dark:border-[var(--border-subtle)] hover:border-[#10B981] text-[#0A2A38] dark:text-[var(--text-primary)] hover:text-[#059669] dark:hover:text-[#10B981]'
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
              <span>Saved to Save Data!</span>
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
        className="flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-white dark:bg-[var(--surface-card)] border border-[#0071A3] hover:bg-[#EBF5FA] dark:hover:bg-[#092535] text-xs font-bold text-[#0071A3] dark:text-[#38BDF8] shadow-xs transition-all duration-150 shrink-0 cursor-pointer"
      >
        <Globe size={15} className="text-[#0071A3] dark:text-[#38BDF8]" />
        <span>Open WebApp Viewer</span>
      </motion.button>
    </footer>
  )
}
