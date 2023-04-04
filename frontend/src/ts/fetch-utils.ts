import { SECONDS } from "./time";

let redirectTimeout = undefined;

export namespace RequireAuth {
  // https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
  const hadAuthError = (response: Response) => {
    return response.status === 401 || response.status === 403;
  };

  const hadUnexpectedError = (response: Response) => {
    // Anything in the range [200, 400) is OK for now
    return !(response.status >= 200 && response.status < 400);
  };

  export const handleFetchError = async (response: Response) => {
    if (hadAuthError(response)) {
      if (redirectTimeout === undefined) {
        redirectTimeout = setTimeout(() => {
          document.location.href = "/api/auth/login";
        }, 1 * SECONDS);
      }
      throw new Error("Session expired, redirecting to login page...");
    } else if (hadUnexpectedError(response)) {
      if (response.headers.get("content-type") === "application/json") {
        const payload = await response.json();
        let error;
        if ("detail" in payload) {
          error = payload["detail"];
          if (!(typeof error === "string")) {
            error = JSON.stringify(error);
          }
        } else {
          error = "An unknown error occurred";
        }
        throw new Error(error);
      } else {
        throw new Error(`${response.status}: "${response.statusText}"`);
      }
    }
    return response;
  };

  export const fetch = async (
    input: URL | RequestInfo,
    init?: RequestInit | undefined
  ) => await handleFetchError(await window.fetch(input, init));

  export const fetchJson = async (
    input: URL | RequestInfo,
    init?: RequestInit | undefined
  ) => await (await RequireAuth.fetch(input, init)).json();
}
