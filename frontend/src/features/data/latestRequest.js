export function createLatestRequestRunner() {
  let generation = 0
  let controller = null

  return {
    async run(operation) {
      controller?.abort()
      controller = new AbortController()
      generation += 1
      const requestGeneration = generation

      try {
        const value = await operation(controller.signal)
        return {
          accepted: requestGeneration === generation,
          value,
        }
      } catch (error) {
        if (requestGeneration !== generation || error.name === 'AbortError') {
          return { accepted: false, value: undefined }
        }
        throw error
      }
    },

    invalidate() {
      generation += 1
      controller?.abort()
      controller = null
    },
  }
}
