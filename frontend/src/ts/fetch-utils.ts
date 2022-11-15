export namespace RequireAuth {
    // https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    const hadAuthError = (response: Response) => {
      return (response.status === 401 || response.status === 403)
    }

    const hadUnexpectedError = (response: Response) => {
      // Anything in the range [200, 400) is OK for now
      return !(response.status >= 200 && response.status < 400)
    }
  
    export const handleFetchError = async (response: Response) => {
      if (hadAuthError(response)) {
        document.location.href = "/api/auth/login"
      } else if (hadUnexpectedError(response)) {
        console.log()
        if (response.headers.get("content-type") === "application/json") {
          const payload = await response.json()
          throw new Error(payload["detail"])
        } else {
          throw new Error(`${response.status}: "${response.statusText}"`)
        }
      }
      return response
    }
  
    export const fetch = async (
      input: URL | RequestInfo,
      init?: RequestInit | undefined
    ) => await handleFetchError(await window.fetch(input, init))
  
    export const fetchJson = async (
      input: URL | RequestInfo,
      init?: RequestInit | undefined
    ) => await (await RequireAuth.fetch(input, init)).json()
  }
  