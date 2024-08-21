import {
  expect,
  describe,
  it,
  jest,
  beforeEach,
  afterAll,
  beforeAll,
} from "@jest/globals";
import type { Job } from "../src/ts/types";
import {
  fetchABL,
  fetchRexReleaseVersion,
  getLatestCodeVersionForBook,
  getLatestCodeVersionForJob,
  getRexReleaseVersion,
  hasABLEntry,
  newABLentry,
} from "../src/ts/abl";
import { errorStore, REXVersionStore } from "../src/ts/stores";
import {
  Fetch,
  approvedBookWithDateFactory,
  bookFactory,
  jobFactory,
  mockJSONResponse,
  mockResponseStatus,
} from "./spec-helpers";

let errors: string[];
const origFetch = window.fetch;
const unsub = errorStore.subscribe((e) => (errors = e));
let fetchSpy: jest.SpiedFunction<Fetch>;
let consoleErrorSpy: jest.SpiedFunction<(...args: unknown[]) => void>;
beforeAll(() => {
  window.fetch = jest.fn<Fetch>();
  fetchSpy = jest.spyOn(window, "fetch");
  consoleErrorSpy = jest.spyOn(console, "error");
});
afterAll(() => {
  window.fetch = origFetch;
  jest.restoreAllMocks();
  unsub();
});
beforeEach(() => {
  // Reset history
  jest.resetAllMocks();
  // Silence error logging
  consoleErrorSpy.mockImplementation(() => {});
  errorStore.clear();
});

describe("newABLentry", () => {
  beforeEach(() => {
    mockResponseStatus(fetchSpy, 200);
  });
  const testCases: { job: Job; code_version: string; expected: any }[] = [
    {
      job: jobFactory.build({
        books: [{ uuid: "fake", slug: "fake-book" }],
        version: "1",
      }),
      code_version: "123",
      expected: [{ uuid: "fake", code_version: "123", commit_sha: "1" }],
    },
    {
      job: jobFactory.build({
        books: [
          { uuid: "fake", slug: "fake-book" },
          { uuid: "fake2", slug: "fake-book" },
        ],
        version: "1",
      }),
      code_version: "1234",
      expected: [
        {
          uuid: "fake",
          code_version: "1234",
          commit_sha: "1",
        },
        {
          uuid: "fake2",
          code_version: "1234",
          commit_sha: "1",
        },
      ],
    },
  ];
  testCases.forEach((args) => {
    it(`calls fetch with the correct information -> ${args}`, async () => {
      const { job, code_version: codeVersion, expected } = args;
      await newABLentry(job, codeVersion);
      const url = fetchSpy.mock.lastCall?.[0];
      const options = fetchSpy.mock.lastCall?.[1];
      const body = JSON.parse(options?.body?.toString() ?? "{}");
      expect(url).toBeDefined();
      expect(errors[0]).toBeUndefined();
      expect(options?.method).toBe("POST");
      expect(options?.headers?.["Content-Type"]).toBe("application/json");
      expect(url).toBe("/api/abl/");
      expect(body).toStrictEqual(expected);
    });
  });
  it("throws a specific error on auth error", async () => {
    const job = jobFactory.build();
    const codeVersion = "1";
    fetchSpy.mockResolvedValue({ status: 403 } as unknown as Response);
    await newABLentry(job, codeVersion);
    expect(errors.length).toBe(1);
    expect(errors[0]).toMatch(/do not.+permission.+entries/i);
  });
});

describe("hasABLEntry", () => {
  it("returns false when the job does not have an approved book", () => {
    const abl = [];
    const job = jobFactory.build();
    expect(hasABLEntry(abl, job)).toBe(false);
  });
  it("returns true when the job does not have an approved book", () => {
    const job = jobFactory.build();
    const abl = [
      approvedBookWithDateFactory.build({
        commit_sha: job.version,
        uuid: job.books[0].uuid,
      }),
    ];
    expect(hasABLEntry(abl, job)).toBe(true);
  });
});

describe("getLatestCodeVersionForBook", () => {
  it("returns the code version of the last book added", () => {
    const uuid = "000000";
    const abl = [...new Array(10)].map(() =>
      approvedBookWithDateFactory.build({ uuid }),
    );
    const book = bookFactory.build({ uuid });
    const latestCodeVersion = abl[abl.length - 1].code_version;
    expect(getLatestCodeVersionForBook(abl, book)).toBe(latestCodeVersion);
  });
  it("returns undefined if the book is not on the abl", () => {
    const uuid = "000000";
    const abl = [];
    const book = bookFactory.build({ uuid });
    expect(getLatestCodeVersionForBook(abl, book)).toBe(undefined);
  });
});

describe("getLatestCodeVersionForJob", () => {
  const uuid = "000000";
  const aBook = bookFactory.build({ uuid });
  const job = jobFactory.build({
    books: [aBook],
  });
  const abl = [...new Array(10)].map(() =>
    approvedBookWithDateFactory.build({ uuid }),
  );
  const latestCodeVersion = abl[abl.length - 1].code_version;
  it("returns the code version of the last book added", () => {
    expect(getLatestCodeVersionForJob(abl, job)).toBe(latestCodeVersion);
  });
  it("returns undefined when job is undefined", () => {
    expect(getLatestCodeVersionForJob(abl, undefined)).toBe(undefined);
  });
  it("returns undefined if any code versions differ in bundle", () => {
    const badUuid = "11111";
    const badAbl = Array.from(abl);
    const badJob = jobFactory.build({
      books: [
        aBook,
        bookFactory.build({
          uuid: badUuid,
        }),
      ],
    });
    badAbl.push(
      approvedBookWithDateFactory.build({
        uuid: badUuid,
      }),
    );
    expect(getLatestCodeVersionForJob(badAbl, badJob)).toBe(undefined);
  });
  it("returns undefined if a job contains no books (should not happen)", () => {
    const badJob = jobFactory.build({ books: [] });
    expect(getLatestCodeVersionForJob(abl, badJob)).toBe(undefined);
  });
});

describe("fetchABL", () => {
  it("fetches the ABL without error", async () => {
    mockJSONResponse(fetchSpy, []);
    const value = await fetchABL();
    const url = fetchSpy.mock.lastCall?.[0];
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(errors[0]).toBeUndefined();
    expect(url).toBe("/api/abl/");
    expect(value).toStrictEqual([]);
  });
  it("sends errors to error store", async () => {
    fetchSpy.mockRejectedValue("test");
    const value = await fetchABL();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(value).toStrictEqual([]);
    expect(errors.length).toBe(1);
    expect(errors[0]).toMatch(/test/);
  });
});

describe("fetchRexReleaseVersion", () => {
  it("fetches the REX release version without error", async () => {
    mockJSONResponse(fetchSpy, { version: "test-version" });
    const version = await fetchRexReleaseVersion();
    const url = fetchSpy.mock.lastCall?.[0];
    expect(errors[0]).toBeUndefined();
    expect(url).toMatch(/rex-release-version/);
    expect(version).toBe("test-version");
  });
  it("returns undefined and sends errors to error store on error", async () => {
    fetchSpy.mockRejectedValue("test");
    const value = await fetchRexReleaseVersion();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(value).toBeUndefined();
    expect(errors.length).toBe(1);
    expect(errors[0]).toMatch(/test/);
  });
  it("only accepts strings", async () => {
    mockJSONResponse(fetchSpy, { version: {} });
    const value = await fetchRexReleaseVersion();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(value).toBeUndefined();
    expect(errors.length).toBe(1);
    expect(errors[0]).toMatch(/Could not get REX release version/);
  });
});

describe("getRexReleaseVersion", () => {
  let updateImmediateSpy: jest.SpiedFunction<() => Promise<void>>;
  let updateSpy: jest.SpiedFunction<() => Promise<void>>;
  // @ts-expect-error baseStore is protected but the test is made reasonably
  // more realistic by violating this visibility rule
  const baseStore = REXVersionStore.baseStore;
  let originalStoreValue;
  baseStore.subscribe((v) => (originalStoreValue = v))();
  beforeAll(() => {
    updateImmediateSpy = jest.spyOn(REXVersionStore, "updateImmediate");
    updateSpy = jest.spyOn(REXVersionStore, "update");
  });
  afterAll(() => {
    jest.restoreAllMocks();
    // Reset store bake to its original value
    baseStore.set(originalStoreValue);
  });
  beforeEach(() => {
    jest.resetAllMocks();
  });
  it("Calls updateImmediate while value is undefined", async () => {
    await getRexReleaseVersion();
    expect(updateImmediateSpy).toHaveBeenCalledTimes(1);
    await getRexReleaseVersion();
    expect(updateImmediateSpy).toHaveBeenCalledTimes(2);
    updateImmediateSpy.mockImplementation(async () => {
      baseStore.set("test-version");
    });
    expect(await getRexReleaseVersion()).toBe("test-version");
    expect(updateSpy).toHaveBeenCalledTimes(0);
    expect(updateImmediateSpy).toHaveBeenCalledTimes(3);
    expect(await getRexReleaseVersion()).toBe("test-version");
    expect(updateSpy).toHaveBeenCalledTimes(1);
    expect(updateImmediateSpy).toHaveBeenCalledTimes(3);
  });
});
