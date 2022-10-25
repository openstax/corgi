import type { Job, RepositorySummary } from "./types"
import { RequireAuth } from "./fetch-utils"

export async function fetchRepos(): Promise<RepositorySummary[]> {
  try {
    return await RequireAuth.fetchJson('/api/github/repository-summary')
  } catch (error) {
    handleFetchError(error)
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

export function calculateElapsed(job: Job): string{
  // let start_time = new Date(job.created_at)
  let update_time = job.status.name == "completed" ? Date.parse(job.updated_at) : Date.now()
  let start_time = Date.parse(job.created_at)
  let elapsed = update_time - start_time
  return `${(Math.floor(elapsed/(60 * 60 * 1000)) % 60).toString().padStart(2, '0')}:${(Math.floor(elapsed/60000) % 60).toString().padStart(2, '0')}:${(elapsed % 60).toString().padStart(2, '0')}`
}