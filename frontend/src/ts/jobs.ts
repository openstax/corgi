import { readableDateTime, handleFetchError } from "./utils"
import type { Job, Status, JobType } from "./types"
import { RequireAuth } from "./fetch-utils"

export async function submitNewJob (jobTypeId: string, repo, book?: string, version?: string, style?: string) {
    // This fails to queue the job silently so the rate limit duration shouldn't
    // be a noticable time period for reasonable usage, else confusion will ensue
    
    let owner = "openstax"
    
    try {
      const data = {
        status_id: 1,
        job_type_id: jobTypeId,
        repository: {
          name: repo,
          owner: owner,
        },
        book: book ? book.trim() : null,
        version: null || version, //(optional)
        style: null || style
      }

      const options = {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
          'Content-Type': 'application/json'
        }
      }

      await RequireAuth.fetch('/api/jobs/', options)
      setTimeout(() => { getJobs() }, 1000)
    } catch (error) {
      RequireAuth.handleAuthError(error)
    }
  }

  export function repeatJob(job: Job) {
    void submitNewJob(job.job_type_id, job.repository.name, null, job.version)
  }

  export async function abortJob(jobId: number) {
    try {
      const data = {
        status_id: "6",
      }

      const options = {
        method: 'PUT',
        body: JSON.stringify(data),
        headers: {
          'Content-Type': 'application/json'
        }
      }

      await RequireAuth.fetch(`/api/jobs/${jobId}`, options)
      setTimeout(() => { getJobs() }, 1000)
    } catch (error) {
      RequireAuth.handleAuthError(error)
    }
  }

  export async function getJobs(): Promise<Job[]> {
    try {
      return await RequireAuth.fetchJson('/api/jobs/')
    } catch (error) {
      RequireAuth.handleAuthError(error)
    }
  }

  export async function getErrorMessage(jobId: number): Promise<string|null> {
    try {
      return await RequireAuth.fetchJson(`/api/jobs/error/${jobId}`)
    } catch (error) {
      RequireAuth.handleAuthError(error)
    }
  }