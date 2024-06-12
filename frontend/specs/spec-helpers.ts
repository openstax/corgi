import * as Factory from "factory.ts";
import type { ApprovedBookWithDate, Book, Job, User } from "../src/ts/types";
import type { jest } from "@jest/globals";

export type Fetch = (
  input: RequestInfo | URL,
  init?: RequestInit | undefined,
) => Promise<Response>;

export type FetchMock = jest.SpiedFunction<Fetch> | jest.Mock<Fetch>;

export const mockResponseStatus = (mock: FetchMock, status: number) => {
  mock.mockResolvedValue({ status } as unknown as Response);
};

export const mockJSONResponse = <T>(mock: FetchMock, json: T, status = 200) => {
  mock.mockResolvedValue({
    status,
    json: async () => json,
  } as unknown as Response);
};

// sfc32 credit: https://pracrand.sourceforge.net/
function sfc32(a: number, b: number, c: number, d: number) {
  return () => {
    a |= 0;
    b |= 0;
    c |= 0;
    d |= 0;
    const t = (((a + b) | 0) + d) | 0;
    d = (d + 1) | 0;
    a = b ^ (b >>> 9);
    b = (c + (c << 3)) | 0;
    c = (c << 21) | (c >>> 11);
    c = (c + t) | 0;
    return (t >>> 0) / 4294967296;
  };
}

export const rng = sfc32(1, 2, 3, 4);

export const randBetween = (rng: () => number, lo: number, hi: number) =>
  rng() * (hi - lo) + lo;

export const toHex = (n: number, padding?: number) =>
  padding === undefined
    ? n.toString(16)
    : n.toString(16).padStart(padding, "0");

export const randHexBetween = (
  rng: () => number,
  lo: number,
  hi: number,
  padding?: number,
) => toHex(Math.floor(randBetween(rng, lo, hi)), padding);

// Not a real uuid4 (missing variant bits)
export const genUuidish = (rng: () => number) =>
  [
    randHexBetween(rng, 0x11111111, 0xffffffff, 8),
    randHexBetween(rng, 0x1111, 0xffff, 4),
    "4" + randHexBetween(rng, 0x111, 0xfff, 3),
    randHexBetween(rng, 0x1111, 0xffff, 4),
    randHexBetween(rng, 0x111111111111, 0xffffffffffff, 12),
  ].join("-");

const uuidishGetter = (count: number) => {
  let uuid = genUuidish(rng);
  return (i: number) => {
    if (i % count === 0) {
      uuid = genUuidish(rng);
    }
    return uuid;
  };
};

const repoGetter = (count: number) => {
  let repo = "osbooks-test-0";
  return (i: number) => {
    if (i % count === 0) {
      repo = `osbooks-test-${i}`;
    }
    return repo;
  };
};

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
  uuid: Factory.each(() => uuidishGetter(3)),
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
    uuid: Factory.each(uuidishGetter(3)),
    slug: "book-slug1",
    code_version: Factory.each((i) => getCodeVersion(i * 1000)),
    consumer: "REX",
    created_at: Factory.each(getCreatedAt),
    commit_sha: Factory.each(() =>
      Math.round(rng() * 100000)
        .toString(16)
        .padStart(7, "0"),
    ),
    committed_at: Factory.each(getCreatedAt),
    repository_name: Factory.each(repoGetter(6)),
  });

export function shuffle<T>(arr: T[]): T[] {
  for (let i = 0; i < arr.length; i++) {
    let swapIdx = i;
    while ((swapIdx = Math.round(rng() * arr.length)) === i);
    const a = arr[i];
    arr[i] = arr[swapIdx];
    arr[swapIdx] = a;
  }
  return arr;
}
