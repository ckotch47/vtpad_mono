/**
 * Simple scoped logger.
 * In production only errors are logged to console.
 * In dev all levels are active.
 */
export function useLogger(scope = '') {
  const prefix = scope ? `[${scope}]` : '[app]'
  const isDev = import.meta.env.DEV

  return {
    error: (msg, err) => {
      console.error(prefix, msg, err)
    },
    warn: (msg, err) => {
      if (isDev) console.warn(prefix, msg, err)
    },
    info: (msg) => {
      if (isDev) console.info(prefix, msg)
    },
    debug: (msg) => {
      if (isDev) console.debug(prefix, msg)
    },
  }
}
