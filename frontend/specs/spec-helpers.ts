import * as Factory from "factory.ts";
import type { ApprovedBookWithDate, Book, Job, User } from "../src/ts/types";
import crypto from "crypto";

// Return datetime in the same format as server
export const getDateTime = (offset: number = 0) =>
  new Date(Date.now() + offset).toISOString().split(".")[0];

// Imperfect recreation of code version
export const getCodeVersion = (offset: number = 0) => {
  const now = new Date(Date.now() + offset);
  return [
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
    ".",
    now.getHours(),
    now.getMinutes(),
    now.getSeconds(),
  ]
    .map((o) => String(o))
    .join("");
};

// Fudge the numbers a little bit to get more realistic results
const getCreatedAt = (i: number) => getDateTime(i * 1000);

export const bookFactory = Factory.Sync.makeFactory<Book>({
  uuid: Factory.each(() => crypto.randomUUID()),
  slug: "book-slug1",
  style: "dummy",
} as unknown as Book);

export const userFactory = Factory.Sync.makeFactory<User>({
  id: Factory.each((i) => String(i)),
  name: Factory.each((i) => `user-${i}`),
  avatar_url: "http://example.com/",
});

export const jobFactory = Factory.Sync.makeFactory<Job>({
  id: Factory.each((i) => i.toString()),
  created_at: Factory.each(getCreatedAt),
  books: [bookFactory.build()],
  git_ref: "main",
  version: Factory.each((i) => i.toString(16)),
  artifact_urls: [],
  error_message: "",
  job_type_id: "1",
  job_type: {
    id: "4",
    name: "git-web-hosting-preview",
    display_name: "Web Preview (git)",
  },
  status_id: "5",
  status: {
    id: "5",
    name: "completed",
  },
  repository: {
    name: "name",
    owner: "owner",
  },
  updated_at: Factory.each(getCreatedAt),
  user: userFactory.build(),
  worker_version: getCodeVersion(),
});

export const approvedBookWithDateFactory =
  Factory.Sync.makeFactory<ApprovedBookWithDate>({
    ...bookFactory.build(),
    code_version: Factory.each((i) => getCodeVersion(i * 1000)),
    consumer: "REX",
    created_at: Factory.each(getCreatedAt),
    commit_sha: Factory.each((i) => i.toString(16)),
    committed_at: Factory.each(getCreatedAt),
    repository_name: Factory.each((i) => `test-${i}`),
  });
