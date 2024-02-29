import { expect, describe, it, jest, beforeEach } from "@jest/globals";
import { submitNewJob, abortJob } from "../src/ts/jobs";
import * as jobs from "../src/ts/jobs";
import { repoToString, parseDateTimeAsUTC } from "../src/ts/utils";
import { jobsStore, updateRunningJobs } from "../src/ts/stores";
import type { Job } from "../src/ts/types";
import { jobFactory } from "./spec-helpers";

let mockFetch;
beforeEach(() => {
  mockFetch = jest
    .fn()
    .mockImplementation(() => Promise.resolve({ status: 200 }));
  window.fetch = mockFetch as any;
});

describe("submitNewJob", () => {
  [
    ["3", "tiny-book", "book-slug1", ""],
    ["4", "tiny-book", "book-slug1", "main"],
    ["3", "owner/repo", "book", "main"],
  ].forEach((args) => {
    it(`calls fetch with the correct information -> ${args}`, () => {
      const [jobTypeId, repo, book, version] = args;
      submitNewJob(jobTypeId, repo, book, version).then(() => {
        const url: string = (mockFetch.mock.lastCall as any[])[0] as string;
        const options = (mockFetch.mock.lastCall as any[])[1];
        const body = JSON.parse(options.body);
        expect(options.method).toBe("POST");
        expect(options.headers["Content-Type"]).toBe("application/json");
        expect(url).toBe("/api/jobs/");
        expect(body.status_id).toBe(1);
        expect(body.job_type_id).toBe(jobTypeId);
        expect(repoToString(body.repository)).toBe(repo);
        expect(body.book).toBe(book || null);
        expect(body.version).toBe(version || null);
      });
    });
  });
});
describe("abortJob", () => {
  it("calls fetch with the correct information", () => {
    const jobId = "1";
    const mockUpdate = jest.fn();
    jobsStore.update = mockUpdate as any;
    window.setTimeout = jest.fn().mockImplementation((fn: any) => {
      fn();
    }) as any;
    abortJob(jobId).then(() => {
      const url: string = (mockFetch.mock.lastCall as any[])[0] as string;
      const options = (mockFetch.mock.lastCall as any[])[1];
      const body = JSON.parse(options.body);
      expect(url).toBe(`/api/jobs/${jobId}`);
      expect(options.method).toBe("PUT");
      expect(body.status_id).toBe("6");
      expect(mockUpdate.mock.calls.length).toBe(1);
    });
  });
});

jest.mock("../src/ts/jobs");

describe("updateRunningJobs", () => {
  const getJobsMock = jobs.getJobs as jest.Mock<() => Promise<Job[]>>;
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it("should get all jobs if no jobs are passed", async () => {
    const jobs = [];
    getJobsMock.mockResolvedValue(jobs);

    const result = await updateRunningJobs(jobs);
    expect(getJobsMock).toHaveBeenCalled();
    expect(result).toStrictEqual(jobs);
  });

  it("should update including and after the oldest running job that was created in the last 24 hours", async () => {
    const jobs: Job[] = [
      jobFactory.build({
        updated_at: new Date(Date.now() - 96400000).toISOString().slice(0, -1),
        created_at: new Date().toISOString().slice(0, -1),
        status: { id: "5" },
      }),
      jobFactory.build({
        updated_at: new Date().toISOString().slice(0, -1),
        created_at: new Date().toISOString().slice(0, -1),
        status: { id: "3" },
      }),
      jobFactory.build({
        updated_at: new Date().toISOString().slice(0, -1),
        created_at: new Date().toISOString().slice(0, -1),
        status: { id: "5" },
      }),
    ];

    getJobsMock.mockResolvedValue([]);

    await updateRunningJobs(jobs);

    expect(getJobsMock).toHaveBeenCalledWith(
      parseDateTimeAsUTC(jobs[1].created_at) / 1000,
    );
  });
});
