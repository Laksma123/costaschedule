import { useEffect, useState } from 'react'

export function usePyBridge() {
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (window.pywebview?.api) {
      setIsReady(true)
      return
    }

    const handleReady = () => setIsReady(true)
    window.addEventListener('pywebviewready', handleReady)
    return () => window.removeEventListener('pywebviewready', handleReady)
  }, [])

  const api = isReady && window.pywebview ? window.pywebview.api : null
  return { isReady, api }
}
