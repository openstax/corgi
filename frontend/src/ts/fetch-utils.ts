import { SECONDS } from "./time";

export interface FetchOptions extends RequestInit {
  handleAuthError?: (response: Response) => Promise<void>;
  handleUnexpectedError?: (response: Response) => Promise<void>;
}

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

  async defaultHandleAuthError() {
    if (this._redirectTimeout === undefined) {
      this._redirectTimeout = setTimeout(() => {
        document.location.href = "/api/auth/login";
      }, 1 * SECONDS);
    }
    throw new Error("Session expired, redirecting to login page...");
  }

  async defaultHandleUnexpectedError(response: Response) {
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

  async handleFetchError(response: Response, options?: FetchOptions) {
    if (_hadAuthError(response)) {
      const handler =
        options?.handleAuthError ?? this.defaultHandleAuthError.bind(this);
      await handler(response);
    } else if (_hadUnexpectedError(response)) {
      const handler =
        options?.handleUnexpectedError ??
        this.defaultHandleUnexpectedError.bind(this);
      await handler(response);
    }
    return response;
  }

  async fetch(input: URL | RequestInfo, options?: FetchOptions | undefined) {
    return await this.handleFetchError(
      await window.fetch(input, options),
      options,
    );
  }

  async fetchJson(
    input: URL | RequestInfo,
    options?: FetchOptions | undefined,
  ) {
    return await (await this.fetch(input, options)).json();
  }

  async sendJson<T>(
    input: URL | RequestInfo,
    body: T,
    options?: FetchOptions | undefined,
  ) {
    const optionsWithContentType = {
      method: "POST",
      body: JSON.stringify(body),
      headers: {
        "Content-Type": "application/json",
      },
      ...options,
    };
    return await this.fetch(input, optionsWithContentType);
  }
})();
