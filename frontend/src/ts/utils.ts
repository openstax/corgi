import type { Job } from "./types";

export function readableDateTime(datetime: string): string {
    return datetime.replace(
        /(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2}).*/,
        ($0, $1, $2, $3, $4) => {
          return `${$1}/${$2}/${$3} ${$4}`
        }
    )
}

export function mapImage(folder: string, name: string): string {
    const index = name.indexOf(' ');
    return `./icons/${folder}/${name.toLowerCase()}.png`; // name.slice(0, index)
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
  // let start_time = new Date(job.created_at);
  let start_time = new Date();
  let update_time = new Date(job.updated_at);
  let elapsed = update_time.getTime() - start_time.getTime();
  return new Date(elapsed * 1000).toISOString().substring(11, 16)
}