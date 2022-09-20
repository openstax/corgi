export function readableDateTime(datetime: string): string {
    return datetime.replace(
        /(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2}).*/,
        ($0, $1, $2, $3, $4) => {
          return `${$1}/${$2}/${$3} ${$4}`
        }
    )
}

export function mapImage(name: string): string {
    const index = name.indexOf(' ');
    return `./icons/${name.slice(0, index).toLowerCase()}.png`;
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