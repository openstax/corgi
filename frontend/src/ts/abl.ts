import { RequireAuth } from "./fetch-utils";
import { REXVersionStore } from "./stores";
import type { Job, Book, ApprovedBookWithDate } from "./types";
import { handleError } from "./utils";
import { parseDateTime } from "./utils";
import * as store from "svelte/store";

export async function newABLentry(job: Job, codeVersion: string | undefined) {
  codeVersion = codeVersion?.trim();
  if (codeVersion === undefined || codeVersion.length === 0) {
    throw new Error("Invalid code version");
  }
  const entries = job.books.map((b) => ({
    uuid: b.uuid,
    code_version: codeVersion,
    commit_sha: job.version,
  }));
  const handleAuthError = () => {
    throw new Error("You do not have permission to add ABL entries.");
  };
  try {
    await RequireAuth.sendJson("/api/abl/", entries, { handleAuthError });
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
    .sort((b, a) => parseDateTime(a.created_at) - parseDateTime(b.created_at));
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
  let abl: ApprovedBookWithDate[];
  try {
    abl = await RequireAuth.fetchJson("/api/abl/");
  } catch (error) {
    handleError(error);
    abl = [];
  }
  return abl;
}

export async function fetchRexReleaseVersion(): Promise<string | undefined> {
  try {
    const resp = await fetch("/api/abl/rex-release-version");
    const { version } = await resp.json();
    if (typeof version !== "string") {
      throw new Error("Could not get REX release version");
    }
    return version;
  } catch (error) {
    handleError(error);
  }
  return undefined;
}

export async function getRexReleaseVersion(): Promise<string | undefined> {
  // If the value is undefined, immediately try to get a new value instead of
  // allowing the update to be deferred
  await (store.get(REXVersionStore) === undefined
    ? REXVersionStore.updateImmediate()
    : REXVersionStore.update());
  return store.get(REXVersionStore);
}
