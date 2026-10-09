import { defineStore } from 'pinia'
import { spaceService } from '@/services'

const EMPTY_CAPABILITIES = Object.freeze({
  cases: false,
  suites: false,
  sections: false,
  plans: false,
  runs: false,
  results: false,
  bugs: false,
  bug_comments: false,
  tags: false,
  tech_docs: false,
  traceability: false,
  run_bug_links: false
})

export const useSpaceCapabilitiesStore = defineStore('spaceCapabilities', {
  state: () => ({ bySpaceId: {}, loadingBySpaceId: {} }),
  actions: {
    async load(spaceId, { force = false } = {}) {
      const id = String(spaceId || '')
      if (!id || id === 'undefined') return EMPTY_CAPABILITIES
      if (!force && this.bySpaceId[id]) return this.bySpaceId[id]
      if (this.loadingBySpaceId[id]) return this.loadingBySpaceId[id]

      const request = spaceService.getById(id)
        .then(({ data }) => {
          const capabilities = { ...EMPTY_CAPABILITIES, ...(data?.capabilities || {}) }
          this.bySpaceId[id] = capabilities
          return capabilities
        })
        .finally(() => {
          delete this.loadingBySpaceId[id]
        })
      this.loadingBySpaceId[id] = request
      return request
    },
    can(spaceId, capability) {
      return this.bySpaceId[String(spaceId || '')]?.[capability] === true
    },
    clear(spaceId) {
      delete this.bySpaceId[String(spaceId || '')]
    }
  }
})
