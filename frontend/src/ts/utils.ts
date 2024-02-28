import type { Job, Repository, RepositorySummary } from "./types";
import { RequireAuth } from "./fetch-utils";
import { errorStore } from "./stores";
import { MINUTES, HOURS, DAYS } from "./time";

type Errors = Error;

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
  return new Date(parseDateTimeAsUTC(datetime)).toLocaleString();
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

export function parseDateTimeAsUTC(dateTime: string) {
  // The database engine we are using does not seem to support storing timezone.
  // We store UTC times in the database. Adding the UTC offset here makes
  // javascript parse the time using UTC timezone instead of local timezone.
  return parseDateTimeAddTZ(dateTime, "+00:00");
}

export function calculateElapsed(job: Job): string {
  const update_time = isJobComplete(job)
    ? parseDateTimeAsUTC(job.updated_at)
    : Date.now();
  const start_time = parseDateTimeAsUTC(job.created_at);
  const elapsed = (update_time - start_time) / 1000;
  const hours = Math.floor(elapsed / 3600)
    .toString()
    .padStart(2, "0");
  const minutes = (Math.floor(elapsed / 60) % 60).toString().padStart(2, "0");
  const seconds = (Math.floor(elapsed) % 60).toString().padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

export function calculateAge(job: Job): string {
  const start_time = parseDateTimeAsUTC(job.created_at);
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
