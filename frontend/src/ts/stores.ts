import { writable } from 'svelte/store'
import type { RepositorySummary } from './types';
import { fetchRepoSummaries } from './utils';

export const error = writable('')
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
        error.set(e.toString())
      } finally {
        fetching = false
      }
    }
  }
})()

