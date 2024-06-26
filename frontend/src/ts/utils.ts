import type { Job, Repository, RepositorySummary } from "./types";
import { RequireAuth } from "./fetch-utils";
import { errorStore } from "./stores";
import { MINUTES, HOURS, DAYS } from "./time";

interface Errors extends Error {}

export function handleError(e: Errors) {
  errorStore.add(e.toString());
  console.error(e);
}

export async function fetchRepoSummaries(): Promise<RepositorySummary[]> {
  let repoSummaries: RepositorySummary[];
  try {
    repoSummaries = await RequireAuth.fetchJson(
      "/api/github/repository-summary",
    );
  } catch (error) {
    handleError(error);
    repoSummaries = [];
  }
  return repoSummaries;
}

export function repoToString(repo: Repository, fullyQualified = false) {
  return !fullyQualified && repo.owner === "openstax"
    ? repo.name
    : `${repo.owner}/${repo.name}`;
}

export function getVersionLink(repository: Repository, version: string) {
  return `https://github.com/${repoToString(repository, true)}/tree/${version}`;
}

export function filterBooks(
  repositories: RepositorySummary[],
  selectedRepo: string,
): string[] {
  const books: string[] = [];
  repositories
    .filter((s) => selectedRepo == "" || repoToString(s).includes(selectedRepo))
    .map((s) => s.books)
    .forEach((bookNames) => {
      bookNames.forEach((b) => books.push(b as any));
    });
  return Array.from(new Set(books));
}

export function readableDateTime(datetime: string): string {
  return new Date(parseDateTime(datetime)).toLocaleString();
}

export function mapImage(folder: string, name: string, type: string): string {
  const index = name.indexOf(" ");
  if (index !== -1) {
    name = name.slice(0, index);
  }
  // console.log(name)
  return `./icons/${folder}/${name.toLowerCase()}.${type}`; // name.slice(0, index)
}

export function isJobComplete(job: Job): boolean {
  return parseInt(job.status.id) >= 4;
}

export function parseDateTimeAddTZ(dateTime: string, tzOffset: string) {
  return Date.parse(dateTime + tzOffset);
}

export const parseDateTime = Date.parse;

export function calculateElapsed(job: Job): string {
  const update_time = isJobComplete(job)
    ? parseDateTime(job.updated_at)
    : Date.now();
  const start_time = parseDateTime(job.created_at);
  const elapsed = (update_time - start_time) / 1000;
  const hours = Math.floor(elapsed / 3600)
    .toString()
    .padStart(2, "0");
  const minutes = (Math.floor(elapsed / 60) % 60).toString().padStart(2, "0");
  const seconds = (Math.floor(elapsed) % 60).toString().padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

export function calculateAge(job: Job): string {
  const start_time = parseDateTime(job.created_at);
  const elapsed = Date.now() - start_time;
  const toCheck: Array<[number, string]> = [
    [DAYS, "days"],
    [HOURS, "hours"],
    [MINUTES, "minutes"],
  ];
  let converted = 0;
  let unit = "N/A";
  let conversion: number;

  for ([conversion, unit] of toCheck) {
    converted = Math.round(elapsed / conversion);
    if (converted >= 1) {
      break;
    }
  }
  return `${converted} ${unit} ago`;
}

// https://stackoverflow.com/a/22706073
export function escapeHTML(str: string) {
  return new Option(str).innerHTML;
}

const compareUnk = <T>(a: T, b: T): number => {
  throw new Error(`Cannot compare ${typeof a} and ${typeof b}`);
};

export function cmp<T>(
  a: T,
  b: T,
  defaultCompare: (a: T, b: T) => number = compareUnk,
): number {
  if (typeof a === "string" && typeof b === "string") {
    return a.localeCompare(b);
  } else if (typeof a === "number" && typeof b === "number") {
    return a - b;
  } else if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return a.length - b.length;
    let n = 0;
    a.some((v, idx) => (n = cmp(v, b[idx], defaultCompare)) !== 0);
    return n;
  } else {
    return defaultCompare(a, b);
  }
}

export function sortBy<T>(
  arr: T[],
  keys: { key: keyof T; desc?: boolean }[],
  customCompare: (a: T[keyof T], b: T[keyof T]) => number = compareUnk,
): T[] {
  return arr.sort((a: T, b: T) => {
    let n = 0;
    for (const { key, desc } of keys) {
      n = cmp(a[key], b[key], customCompare);
      if (desc === true) n *= -1;
      if (n !== 0) break;
    }
    return n;
  });
}

export function buildURL(path: string, query?: Record<string, string>): string {
  const url = new URL("http://origin-not-used");
  url.pathname = path;
  if (query !== undefined) {
    Object.entries(query).forEach(([k, v]) => {
      url.searchParams.append(k, v);
    });
  }
  return url.href.slice(url.origin.length);
}
