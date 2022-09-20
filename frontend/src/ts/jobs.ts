import { readableDateTime, handleFetchError } from "./utils";
import type { Job, Status, JobType } from "./types";

export async function submitNewJob (collectionId, contentServerId, version, astyle, jobType) {
    // This fails to queue the job silently so the rate limit duration shouldn't
    // be a noticable time period for reasonable usage, else confusion will ensue
    
    try {
      const data = {
        collection_id: collectionId,
        status_id: this.jobStatusTypes.Queued,
        pdf_url: null,
        version: version || null,
        style: astyle,
        job_type_id: jobType,
        content_server_id: contentServerId
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

  export async function getJobsForPage(currentPage: number, rowsPerPage: number ): Promise<Job[]> {
    try {
      const httpResponse = await fetch(`/api/jobs/pages/${currentPage}?limit=${rowsPerPage}`) // https://corgi-staging.ce.openstax.org
      let response = await httpResponse.json();
      let items = response.map((entry) => {
        // split collection id to repo and book
        const index = entry.collection_id.lastIndexOf('/');
        entry.repo = entry.collection_id.slice(0, index);
        entry.book = entry.collection_id.slice(index + 1);

        // format timestamps
        entry.created_at = readableDateTime(entry.created_at);
        let start_time = new Date(entry.created_at);
        let update_time = new Date(entry.updated_at);
        let elapsed = update_time.getTime() - start_time.getTime();
        entry.elapsed = new Date(elapsed * 1000).toISOString().substring(11, 16)

        return entry; 
      })
      return items;
      // slice = items.slice(start, end);
    } catch (error) {
      handleFetchError(error);
    }
  }