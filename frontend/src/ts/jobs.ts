import { readableDateTime, handleFetchError } from "./utils";
import type { Job, Status, JobType } from "./types";

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
        book: null || book,
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

      await fetch('/api/jobs/', options);
      setTimeout(() => { this.getJobsImmediate() }, 1000)
    } catch (error) {
      console.log(error)
    }
  }

  export async function getJobs(): Promise<Job[]> {
    try {
      // const httpResponse = await fetch(`/api/jobs/pages/${currentPage}?limit=${rowsPerPage}`) // https://corgi-staging.ce.openstax.org
      const httpResponse = await fetch("/jobs.json");
      return await httpResponse.json();
    } catch (error) {
      handleFetchError(error);
    }
  }

  // export async function submitNewJob(jobTypeId: string, repo, book?: string, version?: string, style?: string) {
  //   try {
  //     //split repo name for owner default to openstax
  //     let owner = "openstax"

  //     const payload = {
  //       status_id: 1,
  //       job_type_id: jobTypeId,
  //       repository: {
  //         name: repo,
  //         owner: owner,
  //       },
  //       book: null || book,
  //       version: null || version, //(optional)
  //       style: null || style
  //     }

  //     const httpResponse await fetch("/api/jobs/", { data: payload })
  //   } catch (error) {
  //     handleFetchError(error);
  //   }
  // }

  // export async function updateJob(params:type) {
  //   try {
  //     const httpResponse await fetch("/api/jobs/")
  //   } catch (error) {
  //     handleFetchError(error);
  //   }
  // }