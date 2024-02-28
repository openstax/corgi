import { RequireAuth } from "./fetch-utils";
import type { Job, Book, ApprovedBookWithDate } from "./types";
import { handleError } from "./utils";
import { parseDateTimeAsUTC } from "./utils";

export async function newABLentry(job: Job, codeVersion: string) {
  const guessConsumer = (b: Book) =>
    b.slug.match(/-(ancillaries|ancillary)$/) != null ? "ancillary" : "REX";
  const entries = job.books.map((b) => ({
    uuid: b.uuid,
    code_version: codeVersion,
    commit_sha: job.version,
    consumer: guessConsumer(b),
  }));
  const options = {
    method: "POST",
    body: JSON.stringify(entries),
    headers: {
      "Content-Type": "application/json",
    },
  };
  try {
    await RequireAuth.fetch("/api/abl/", options);
  } catch (error) {
    handleError(error);
  }
}

export function hasABLEntry(abl: ApprovedBookWithDate[], job: Job) {
  // If the approved book matches the job's commit sha
  // and any of the books match
  return abl.some(
    (approvedBook) =>
      approvedBook.commit_sha === job.version &&
      job.books.some((jobBook) => approvedBook.uuid == jobBook.uuid),
  );
}

export function getLatestCodeVersionForBook(
  abl: ApprovedBookWithDate[],
  book: Book,
) {
  const latestEntry = abl
    .filter((entry) => entry.uuid === book.uuid)
    .sort(
      (b, a) =>
        parseDateTimeAsUTC(a.created_at) - parseDateTimeAsUTC(b.created_at),
    );
  return latestEntry[0]?.code_version;
}

export function getLatestCodeVersionForJob(
  abl: ApprovedBookWithDate[],
  job: Job | undefined,
) {
  if (job === undefined) {
    return undefined;
  }
  const codeVersions = job.books.map((b) =>
    getLatestCodeVersionForBook(abl, b),
  );
  let codeVersion: string | undefined = codeVersions[0];
  for (const latestCodeVersion of codeVersions) {
    if (latestCodeVersion !== codeVersion) {
      return undefined;
    }
    codeVersion = latestCodeVersion;
  }
  return codeVersion;
}

export async function fetchABL(): Promise<ApprovedBookWithDate[]> {
  let abl: any;
  try {
    abl = await RequireAuth.fetchJson("/api/abl/");
  } catch (error) {
    handleError(error);
    abl = [];
  }
  return abl;
}
