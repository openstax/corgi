import type { Job, RepositorySummary } from "./types"

export async function fetchRepos(): Promise<RepositorySummary[]> {
  try {
    let httpResponse = await fetch('/api/github/repository-summary')
    return await httpResponse.json()
  } catch (error) {
    console.log("OOF")
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
    console.log(name)
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
  let start_time = new Date()
  let update_time = new Date(job.updated_at)
  let elapsed = update_time.getTime() - start_time.getTime()
  return new Date(elapsed * 1000).toISOString().substring(11, 16)
}