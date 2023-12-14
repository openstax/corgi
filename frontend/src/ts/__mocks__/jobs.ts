import { jest } from "@jest/globals";

const jobs = jest.requireActual("../jobs");
(jobs as any).getJobs = jest.fn();

module.exports = jobs;
