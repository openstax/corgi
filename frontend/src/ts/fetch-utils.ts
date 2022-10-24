export namespace RequireAuth {
    const ERROR_CODEs = [401, 403]
  
    export const handleAuthError = (response: Response) => {
      if (ERROR_CODEs.indexOf(response.status) !== -1) {
        document.location.href = "/api/auth/login"
        throw new Error(response.statusText)
      }
      return response
    }
  
    export const fetch = async (
      input: URL | RequestInfo,
      init?: RequestInit | undefined
    ) => handleAuthError(await window.fetch(input, init))
  
    export const fetchJson = async (
      input: URL | RequestInfo,
      init?: RequestInit | undefined
    ) => await (await RequireAuth.fetch(input, init)).json()
  }
  