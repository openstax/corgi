import { SECONDS } from "./time";

// https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
const _hadUnexpectedError = (response: { status: number }) => {
  // Anything in the range [200, 400) is OK for now
  return !(response.status >= 200 && response.status < 400);
};

const _hadAuthError = (response: { status: number }) => {
  return response.status === 401 || response.status === 403;
};

export const RequireAuth = new (class {
  private _redirectTimeout: NodeJS.Timeout | undefined = undefined;

  async handleFetchError(response: Response) {
    if (_hadAuthError(response)) {
      if (this._redirectTimeout === undefined) {
        this._redirectTimeout = setTimeout(() => {
          document.location.href = "/api/auth/login";
        }, 1 * SECONDS);
      }
      throw new Error("Session expired, redirecting to login page...");
    } else if (_hadUnexpectedError(response)) {
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
  }

  async fetch(input: URL | RequestInfo, init?: RequestInit | undefined) {
    return await this.handleFetchError(await window.fetch(input, init));
  }

  async fetchJson(input: URL | RequestInfo, init?: RequestInit | undefined) {
    return await (await this.fetch(input, init)).json();
  }
})();
