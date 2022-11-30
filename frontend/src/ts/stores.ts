import { writable } from 'svelte/store'
import type { RepositorySummary } from './types';
import { fetchRepoSummaries } from './utils';

export const errorStore = (() => {
  const { subscribe, set } = writable([] as string[])
  const errors: string[] = []
  return {
    subscribe,
    add: (err: string) => {
      const now = new Date()
      errors.unshift(`${now.toLocaleTimeString()} - ${err}`)
      set(errors)
    },
    clear: () => {
      errors.splice(0)
      set(errors)
    }
  }
})()

export const repoSummariesStore = (() => {
  const { subscribe, set } = writable([] as RepositorySummary[])
  let fetching = false
  return {
    subscribe,
    update: async () => {
      if (fetching) {
        return
      }
      try {
        console.log("Fetching repository summaries")
        fetching = true
        set(await fetchRepoSummaries())
      } catch (e) {
        errorStore.add(e.toString())
      } finally {
        fetching = false
      }
    }
  }
})()

