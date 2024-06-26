import {
  expect,
  describe,
  it,
  jest,
  beforeEach,
  beforeAll,
  afterAll,
} from "@jest/globals";
import { Fetch, mockJSONResponse, mockResponseStatus } from "./spec-helpers";
import { getBookRepo } from "../src/ts/repository";

const origFetch = window.fetch;
let fetchSpy: jest.SpiedFunction<Fetch>;
beforeAll(() => {
  window.fetch = jest.fn<Fetch>();
  fetchSpy = jest.spyOn(window, "fetch");
});
afterAll(() => {
  window.fetch = origFetch;
  jest.restoreAllMocks();
});
beforeEach(() => {
  // Reset history
  jest.resetAllMocks();
  mockResponseStatus(fetchSpy, 200);
});

describe("getBookRepo", () => {
  it("gets Book Repo", async () => {
    const mockResponse = ["bookRepo", "ref", "committedAt", "books"];
    mockJSONResponse(fetchSpy, mockResponse);
    const fakeResponse = await getBookRepo({ name: "test", owner: "ing" });
    const expectedURL = "/api/github/book-repository/ing/test";
    const expectedOptions = undefined;
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy).toHaveBeenCalledWith(expectedURL, expectedOptions);
    // Should return an object with "bookRepo", "ref", "committedAt", "books"
    expect(fakeResponse).toStrictEqual(
      Object.fromEntries(mockResponse.map((v) => [v, v])),
    );
  });
});
