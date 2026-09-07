import { motion } from 'motion/react'
import { Lock, Copy, Activity } from 'lucide-react'

export default function PayloadTab({ payload, telemetry, onCopyPayload }) {
  const chars = telemetry?.payloadChars || 0
  const b64 = telemetry?.b64Bytes || 0

  return (
    <div className="h-full flex flex-col p-4">
      {/* Info Bar */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Lock size={14} className="text-[var(--accent-color)]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[var(--accent-color)]">
            Encrypted Transmission Stream
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-[var(--text-subtle)] font-mono">
            <Activity size={12} />
            {chars.toLocaleString()} chars · {b64.toLocaleString()} bytes encoded
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            onClick={onCopyPayload}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold
              bg-[var(--surface-inner)] hover:bg-[var(--surface-hover)]
              border border-[var(--border-subtle)]
              text-[var(--text-primary)] transition-colors duration-150 cursor-pointer"
          >
            <Copy size={12} />
            Copy Stream
          </motion.button>
        </div>
      </div>

      {/* Payload Text */}
      <div className="flex-1 min-h-0 rounded-xl border border-[var(--border-subtle)] bg-[var(--surface-inner)] overflow-auto">
        <pre className="p-4 text-xs font-mono text-[var(--text-primary)] whitespace-pre-wrap break-all leading-relaxed select-text">
          {payload || 'No payload generated. Load and process a schedule file first.'}
        </pre>
      </div>
    </div>
  )
}
