"""
Docker Hub API client using httpx.

This module provides a small helper class that can fetch the newest image
tags for a given Docker Hub repository.  The implementation uses the
public Docker Hub REST API (v2) and the `httpx` HTTP client.

The main entry point is :func:`DockerHubAPI.get_newest_tags`.  It returns
a list of tag names ordered from newest to oldest.  The caller specifies
how many tags to retrieve, and can optionally provide a regex to filter
results.

"""

import re
from typing import TypedDict

import httpx

API_BASE = "https://hub.docker.com/v2"


class FetchOptions(TypedDict, total=False):
    ordering: str
    pattern: str


class DockerHubAPI:
    """Client for Docker Hub API v2.

    Parameters
    ----------
    timeout:
        Optional timeout in seconds for HTTP requests.
    """

    def __init__(self, timeout: float | None = 10.0) -> None:
        self.timeout = timeout

    @property
    def client(self):
        return httpx.AsyncClient(timeout=self.timeout)

    async def _fetch_tags_page(
        self,
        namespace: str,
        repo: str,
        page_size: int,
        page: int,
        ordering: str,
    ) -> dict:
        """Fetch a single page of tags.

        Parameters
        ----------
        namespace:
            Docker Hub namespace (e.g. ``library`` for official images).
        repo:
            Repository name.
        page_size:
            Number of tags per page.
        page:
            Page number (1-indexed).
        ordering:
            Sort results by this.
        """
        url = f"{API_BASE}/repositories/{namespace}/{repo}/tags/"
        params = {
            "page_size": page_size,
            "page": page,
            "ordering": ordering,
        }
        async with self.client as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    async def get_newest_tags(
        self, repo: str, count: int, options: FetchOptions | None = None
    ) -> list[str]:
        """Return the `count` newest tags for `repo`, optionally filtered by
        regex.

        Parameters
        ----------
        repo:
            Full repository name in the form ``namespace/repo``.
            If only ``repo`` is provided, ``library`` is assumed.
        count:
            Number of tags to return.
        options:
            pattern: regex str
            ordering; how to sort results
        """
        if "/" in repo:
            namespace, repo_name = repo.split("/", 1)
        else:
            namespace, repo_name = "library", repo
        options = options if options is not None else {}
        pattern = options.get("pattern", None)
        ordering = options.get("ordering", "last_updated")

        tags: list[str] = []
        page = 1
        page_size = min(count, 100)  # Docker Hub limits page_size to 100
        while len(tags) < count:
            data = await self._fetch_tags_page(
                namespace, repo_name, page_size, page, ordering
            )
            results = data.get("results", [])
            if not results:
                break
            for entry in results:
                name = entry.get("name")
                if name and (pattern is None or re.match(pattern, name)):
                    tags.append(name)
                if len(tags) >= count:
                    break
            if not data.get("next"):
                break
            page += 1
        return tags[:count]


api = DockerHubAPI()
