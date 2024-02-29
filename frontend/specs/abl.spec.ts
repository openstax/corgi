import {
  expect,
  describe,
  it,
  jest,
  beforeEach,
  afterAll,
} from "@jest/globals";
import type { Job } from "../src/ts/types";
import {
  fetchABL,
  getLatestCodeVersionForBook,
  getLatestCodeVersionForJob,
  hasABLEntry,
  newABLentry,
} from "../src/ts/abl";
import { errorStore } from "../src/ts/stores";
import {
  approvedBookWithDateFactory,
  bookFactory,
  jobFactory,
} from "./spec-helpers";

describe("newABLentry", () => {
  let mockFetch;
  let errors: string[];
  const unsub = errorStore.subscribe((e) => (errors = e));
  beforeEach(() => {
    mockFetch = jest
      .fn<() => Promise<Response>>()
      .mockResolvedValue({ status: 200 } as unknown as Response);
    window.fetch = mockFetch as any;
    errorStore.clear();
  });
  afterAll(() => {
    unsub();
  });
  const testCases: { job: Job; code_version: string; expected: any }[] = [
    {
      job: jobFactory.build({
        books: [{ uuid: "fake", slug: "fake-book" }],
        version: "1",
      }),
      code_version: "123",
      expected: [
        { uuid: "fake", code_version: "123", commit_sha: "1", consumer: "REX" },
      ],
    },
    {
      job: jobFactory.build({
        books: [
          { uuid: "fake", slug: "fake-book" },
          { uuid: "fake2", slug: "fake-book-ancillary" },
        ],
        version: "1",
      }),
      code_version: "1234",
      expected: [
        {
          uuid: "fake",
          code_version: "1234",
          commit_sha: "1",
          consumer: "REX",
        },
        {
          uuid: "fake2",
          code_version: "1234",
          commit_sha: "1",
          consumer: "ancillary",
        },
      ],
    },
  ];
  testCases.forEach((args) => {
    it(`calls fetch with the correct information -> ${args}`, async () => {
      const { job, code_version: codeVersion, expected } = args;
      await newABLentry(job, codeVersion);
      const url: string = (mockFetch.mock.lastCall as any[])[0] as string;
      const options = (mockFetch.mock.lastCall as any[])[1];
      const body = JSON.parse(options.body);
      expect(errors[0]).toBeUndefined();
      expect(options.method).toBe("POST");
      expect(options.headers["Content-Type"]).toBe("application/json");
      expect(url).toBe("/api/abl/");
      expect(body).toStrictEqual(expected);
    });
  });
  it("throws a specific error on auth error", async () => {
    const job = jobFactory.build();
    const codeVersion = "1";
    window.fetch = jest
      .fn<() => Promise<Response>>()
      .mockResolvedValue({ status: 403 } as unknown as Response);
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
  let mockFetch;
  let errors: string[];
  const unsub = errorStore.subscribe((e) => (errors = e));
  beforeEach(() => {
    mockFetch = jest.fn<() => Promise<Response>>().mockResolvedValue({
      status: 200,
      json: async () => [],
    } as unknown as Response);
    window.fetch = mockFetch as any;
    errorStore.clear();
  });
  afterAll(() => {
    unsub();
  });
  it("fetches", async () => {
    const value = await fetchABL();
    const url: string = (mockFetch.mock.lastCall as any[])[0] as string;
    expect(errors[0]).toBeUndefined();
    expect(url).toBe("/api/abl/");
    expect(value).toStrictEqual([]);
  });
});
