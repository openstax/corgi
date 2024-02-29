import { handleError, repoToString } from "./utils";
import type { Job } from "./types";
import { RequireAuth } from "./fetch-utils";
import { SECONDS } from "./time";
import { jobsStore } from "./stores";

export async function submitNewJob(
  jobTypeId: string,
  repo: string,
  book?: string | null,
  version?: string | null,
) {
  // This fails to queue the job silently so the rate limit duration shouldn't
  // be a noticable time period for reasonable usage, else confusion will ensue
  try {
    let owner = "openstax";
    if (repo.indexOf("/") !== -1) {
      const splitRepo = repo.split("/");
      if (splitRepo.length !== 2) {
        throw new Error("Invalid repository");
      }
      owner = splitRepo[0];
      repo = splitRepo[1];
    }

    const data = {
      status_id: 1,
      job_type_id: jobTypeId,
      repository: {
        name: repo,
        owner: owner,
      },
      book: (book?.trim() ?? "") || null, // null means all books
      version: (version?.trim() ?? "") || null, //(optional)
    };

    await RequireAuth.sendJson("/api/jobs/", data);
  } catch (error) {
    handleError(error);
  }
}

export function repeatJob(job: Job) {
  void submitNewJob(
    job.job_type_id,
    repoToString(job.repository),
    job.books.length === 1 ? job.books[0].slug : null,
    job.git_ref,
  );
}

export async function abortJob(jobId: string) {
  try {
    const data = {
      status_id: "6",
    };

    await RequireAuth.sendJson(`/api/jobs/${jobId}`, data, { method: "PUT" });
    setTimeout(() => {
      void jobsStore.update();
    }, 1 * SECONDS);
  } catch (error) {
    handleError(error);
  }
}

export async function getJobs(start?: number): Promise<Job[]> {
  let jobs: Job[];
  try {
    const query_url =
      start == null ? "/api/jobs/" : `/api/jobs/?range_start=${start}`;
    jobs = await RequireAuth.fetchJson(query_url);
  } catch (error) {
    handleError(error);
    jobs = [];
  }
  return jobs;
}

export async function getErrorMessage(jobId: string): Promise<string | null> {
  let error: string;
  try {
    error = await RequireAuth.fetchJson(`/api/jobs/error/${jobId}`);
  } catch (fetchError) {
    handleError(fetchError);
    error = "";
  }
  return error;
}
