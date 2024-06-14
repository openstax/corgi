import { RequireAuth } from "./fetch-utils";
import type { Repository } from "./types";

export async function getBookRepo(repo: Repository, version: string = "main") {
  const [bookRepo, ref, commitedAt, books] = await RequireAuth.fetchJson(
    `/api/github/book-repository/${repo.owner}/${repo.name}?version=${version}`,
  );
  return {
    bookRepo,
    ref,
    commitedAt,
    books,
  };
}

export async function isRepoPubic(repo: Repository) {
  const { bookRepo } = await getBookRepo(repo);
  return bookRepo.visibility === "PUBLIC";
}
