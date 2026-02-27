# Pipeline Management Backend

This document explains the backend components added to support the webhosting pipeline admin interface (CORE-1621).

---

## Overview

The goal is to maintain three concurrent Concourse webhosting pipelines at different code versions (newest, second, oldest). CORGI tracks which versions are active and exposes endpoints so that:

- A **Concourse metapipeline** can poll for version changes and update itself accordingly.
- An **admin UI** can view and update the active versions.
- Admins can browse available Docker Hub image tags to choose from.

---

## Database: `PipelineVersion` table

`backend/app/app/db/schema.py`

```python
class PipelineVersion(Base):
    code_version_id = sa.Column(sa.ForeignKey("code_version.id"), primary_key=True)
    position        = sa.Column(sa.Integer, nullable=False)
    created_at      = sa.Column(DateTimeUTC, ...)
    updated_at      = sa.Column(DateTimeUTC, ...)

    code_version = relationship("CodeVersion", ...)

    __table_args__ = (
        sa.UniqueConstraint("position", name="_unique_pipeline_position"),
    )
```

- **`code_version_id`** — Foreign key into the existing `CodeVersion` table, which is shared with the ABL. This avoids duplicating version strings.
- **`position`** — Integer slot: `0` = newest, `1` = second, `2` = oldest. A unique constraint ensures no two rows share the same slot.
- There is no `user_id`. An audit trail was considered but excluded from scope.

### Why delete-all and re-insert?

Swapping positions between existing rows would violate the unique constraint mid-transaction (e.g. moving `0→1` while `1` still exists). The simplest correct solution is to delete all rows and re-insert the desired state in a single transaction. The table is tiny (max 3 rows) so this is not a performance concern.

---

## Endpoint: `GET /api/pipeline-version/`

`backend/app/app/api/endpoints/pipeline_version.py`

- **Auth:** None required (intentionally public, like `GET /api/jobs/{id}`).
- **Purpose:** The Concourse metapipeline polls this endpoint to detect version changes.
- **Returns:** The three active pipeline versions ordered by position.

```json
[
  {"position": 0, "version": "20260223.201034"},
  {"position": 1, "version": "20260221.000200"},
  {"position": 2, "version": "20260219.150716"}
]
```

---

## Endpoint: `PUT /api/pipeline-version/`

`backend/app/app/api/endpoints/pipeline_version.py`

- **Auth:** Admin only (`Role.ADMIN`).
- **Purpose:** Replaces the entire set of active pipeline versions.
- **Body:** Same shape as the GET response — a list of `{position, version}` objects.
- **Validation:** Rejects the request if the same version string appears in more than one slot.
- **Behavior:** Deletes all existing rows, then re-inserts the submitted set in a single transaction. Uses `get_or_add_code_version` (shared with the ABL) to look up or create the corresponding `CodeVersion` row.

---

## Endpoint: `GET /api/version/tags/{repo}`

`backend/app/app/api/endpoints/version.py`

- **Auth:** Authenticated users (`Role.USER`).
- **Purpose:** Returns recent Docker Hub image tags for a given repository, for use in the admin UI's select boxes.
- **Allowed repos:** Only `openstax::enki` (double-colon is converted to `/` for the Docker Hub API call).
- **Parameters:**
  - `count` — how many tags to return (max 25).
  - `pattern` — regex filter applied to tag names (default: `^\d+\.\d+$`).
- **Returns:**
  ```json
  {"items": ["20260225.221405", "20260223.201034", ...], "count": 5, "current_version": null}
  ```
  `current_version` is non-null when one of the returned tags matches the deployed version of CORGI itself (from `TAG` config).
- **Caching:** Results are memoized for 5 minutes via `async_memoize_timed` to avoid hammering the Docker Hub API.

---

## Service: Docker Hub API client

`backend/app/app/service/docker_hub.py`

A small `httpx`-based async client that calls the Docker Hub v2 REST API.

- Fetches tags for `{namespace}/{repo}`, paginating as needed.
- Sorts by `last_updated` (most recent first) by default.
- Optionally filters tag names against a regex pattern before returning.
- Page size is capped at 100 (Docker Hub's limit); pagination stops early once `count` tags have been collected.

---

## Utility: `async_memoize_timed`

`backend/app/app/api/utils.py`

A TTL-based memoization decorator for async functions. Cache entries expire on a fixed-period clock boundary (not from the time of the last call), so all callers see a refresh at the same time. The cache is bounded by `maxsize` entries (default 25) using a ring-buffer eviction policy.
