import type { Job, RepositorySummary } from "./types"
import { RequireAuth } from "./fetch-utils"
import { error } from './stores'

type Errors = Error

export function handleError(e: Errors) {
  error.update(_ => e.toString())
  console.error(e)
}

export async function fetchRepos(): Promise<RepositorySummary[]> {
  try {
    return await RequireAuth.fetchJson('/api/github/repository-summary')
  } catch (error) {
    handleError(error)
    throw error
  }
}

export function filterBooks(repositories: RepositorySummary[], selectedRepo: string): string[] {
  let books: string[] = []
  repositories
    .filter(s => selectedRepo == '' || s.name.includes(selectedRepo))
    .map(s => s.books)
    .forEach(bookNames => {
      bookNames.forEach(b => books.push((b as any)))
    })
  console.log(books)
  return books
}

export function readableDateTime(datetime: string): string {
    return datetime.replace(
        /(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2}).*/,
        ($0, $1, $2, $3, $4) => {
          return `${$1}/${$2}/${$3} ${$4}`
        }
    )
}

export function mapImage(folder: string, name: string, type: string): string {
    const index = name.indexOf(' ')
    // console.log(name)
    return `./icons/${folder}/${name.toLowerCase()}.${type}` // name.slice(0, index)
}

export function handleFetchError (error) {
    // this is optional and mostly for debugging on dev mode
    if (error.response) {
      // Request made and server responded
      console.log(error.response.data)
      console.log(error.response.status)
      console.log(error.response.headers)
    } else if (error.request) {
      // The request was made but no response was received
      console.log(error.request)
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Error', error.message)
    }
    throw error
  }

export function isJobComplete(job: Job): boolean {
  return parseInt(job.status.id) >= 4
}

function parseDateAddTZ(time: string, tzOffset: string = '00:00') {
  return Date.parse(`${time}+${tzOffset}`)
}

export function calculateElapsed(job: Job): string{
  // let start_time = new Date(job.created_at)
  let update_time = isJobComplete(job)
    ? parseDateAddTZ(job.updated_at)
    : Date.now()
  let start_time = parseDateAddTZ(job.created_at)
  let elapsed = (update_time - start_time) / 1000
  const hours = Math.floor(elapsed / 3600).toString().padStart(2, '0')
  const minutes = (Math.floor(elapsed / 60) % 60).toString().padStart(2, '0')
  const seconds = (Math.floor(elapsed) % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

export async function newABLentry (job: Job) {
  const repo = job.repository
  if (repo.owner !== 'openstax') {
    const errMsg = 'Only Openstax repositories can be added to the ABL at this time'
    alert(errMsg)
    throw new Error(errMsg)
  }
  const ablData = await (await fetch(`/api/abl/${repo.name}/${job.version}`)).json()

  // What goes inside the versions array
  const versionEntry = {
    min_code_version: null, // To be filled in manually
    edition: null, // To be filled in manually
    commit_sha: ablData.commit_sha,
    commit_metadata: {
      committed_at: ablData.committed_at,
      books: ablData.books
    }
  }

  // Line number is 1 for new ABL entries
  const ablEntry = ablData.line_number === 1
    ? {
        repository_name: repo.name,
        platforms: ['REX'],
        versions: [
          versionEntry
        ]
      }
    : versionEntry

  await navigator.clipboard.writeText(JSON.stringify(ablEntry, null, 2))
  window.open(`https://github.com/openstax/content-manager-approved-books/edit/main/approved-book-list.json#L${ablData.line_number}`, '_blank')
}