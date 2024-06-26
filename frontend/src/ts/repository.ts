import { RequireAuth } from "./fetch-utils";
import type { BookRepository, Repository } from "./types";
import { buildURL } from "./utils";

export async function getBookRepo(
  repo: Repository,
  query?: { version?: string },
): Promise<BookRepository> {
  const url = buildURL(
    `/api/github/book-repository/${repo.owner}/${repo.name}`,
    query,
  );
  const [bookRepo, ref, committedAt, books] = await RequireAuth.fetchJson(url);
  return {
    bookRepo,
    ref,
    committedAt,
    books,
  };
}

export async function isRepoPubic(repo: Repository) {
  const { bookRepo } = await getBookRepo(repo);
  return bookRepo.visibility === "PUBLIC";
}
