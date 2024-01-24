import { expect, describe, it, jest } from "@jest/globals";
import { RequireAuth } from "../src/ts/fetch-utils";

describe("fetch", () => {
  [401, 403].forEach((status) => {
    it(`throws an exception on auth error -> ${status}`, () => {
      const mockFetch = jest
        .fn()
        .mockImplementation(() => Promise.resolve({ status }));
      const mockTimeout = jest.fn();
      window.fetch = mockFetch as any;
      window.setTimeout = mockTimeout as any;
      RequireAuth.fetch("/")
        .then(() => {
          throw new Error(`${status} should cause exception`);
        })
        .catch((err) => {
          expect(err.toString()).toContain("expired");
          expect(mockTimeout.mock.calls.length).toBe(1);
        });
    });
  }),
    [100, 404, 500].forEach((status) => {
      it(`throws an exception on status not in range [200, 400) -> ${status}`, () => {
        const statusText = "testing errors";
        const mockFetch = jest.fn().mockImplementation(() =>
          Promise.resolve({
            status,
            statusText,
            json: async () => ({}),
            headers: new Map(),
          }),
        );
        const mockTimeout = jest.fn();
        window.fetch = mockFetch as any;
        window.setTimeout = mockTimeout as any;
        RequireAuth.fetch("/")
          .then(() => {
            throw new Error(`${status} should cause exception`);
          })
          .catch((err) => {
            const errString = err.toString();
            expect(errString).toContain(status.toString());
            expect(errString).toContain(statusText);
            expect(mockTimeout.mock.calls.length).toBe(0);
          });
      });
    }),
    [
      { type: "string", error: { detail: "Error" } },
      { type: "json", error: { detail: { nestedError: "test" } } },
      { type: "unknown", error: {} },
    ].forEach(({ type, error }) => {
      it(`surfaces error details -> ${type}`, () => {
        const mockFetch = jest.fn().mockImplementation(() =>
          Promise.resolve({
            status: 500,
            json: async () => error,
            headers: new Map([["content-type", "application/json"]]),
          }),
        );
        const mockTimeout = jest.fn();
        window.fetch = mockFetch as any;
        window.setTimeout = mockTimeout as any;
        RequireAuth.fetch("/")
          .then(() => {
            throw new Error("should cause exception");
          })
          .catch((err) => {
            const errString = err.toString();
            const expectedError =
              type === "unknown"
                ? "unknown"
                : type === "json"
                  ? JSON.stringify(error.detail)
                  : error.detail;
            expect(errString).toContain(expectedError);
            expect(mockTimeout.mock.calls.length).toBe(0);
          });
      });
    });
});
describe("fetchJson", () => {
  it("returns json responses directly", () => {
    const obj = { a: 1, b: 2, c: 3 };
    const mockFetch = jest.fn().mockImplementation(() =>
      Promise.resolve({
        status: 200,
        json: async () => obj,
      }),
    );
    window.fetch = mockFetch as any;
    RequireAuth.fetchJson("/")
      .then((ret) => {
        expect(ret).toBe(obj);
      })
      .catch((err) => {
        throw err;
      });
  });
});
