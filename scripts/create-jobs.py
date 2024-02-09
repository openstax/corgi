import asyncio
from time import strftime
import sys

from httpx import AsyncClient


async def main():
    token = sys.argv[1]
    worker_version = strftime("%Y%m%d.%H%M%S+dev")
    async with AsyncClient() as client:
        response = await client.get(
            "http://localhost/api/auth/token-login",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=True,
        )
        if response.cookies.get("session", None) is None:
            exit("Could not get session cookie")
        created_jobs = [
            {
                "status_id": "1",
                "job_type_id": job_type_id,
                "repository": {"name": "tiny-book", "owner": "openstax"},
                "book": "book-slug1",
                "worker_version": worker_version,
            }
            for job_type_id in ((3, 4, 5, 6) * 2)
        ]
        responses = await asyncio.gather(
            *[
                client.post("http://localhost/api/jobs/", json=job_args)
                for job_args in created_jobs
            ]
        )
        for response in responses:
            response.raise_for_status()
            print("Job created!")
        # I would like to update the last 5 jobs (sort by id)
        jobs = sorted((r.json() for r in responses), key=lambda j: j["id"])
        to_update = []
        # Update a job to each status (queued exists, so only do last 5)
        for i, job in enumerate(jobs[-5:]):
            # Add 1 becuase ids start at 1, add 1 again to skip queued
            status_id = i + 2
            job_id = job["id"]
            update_args = {"status_id": str(status_id)}
            if status_id == 4:
                lines = (
                    "+ Trace line",
                    "+ Trace line 2",
                    "Just testing",
                    "1",
                    "2",
                    "3",
                    "Error ./modules/m123/index.cnxml:3:1 "
                    "<!-- here and ./modules/m123/index.cnxml:3:1 <-- here",
                    '<a href="escaped">Should-not-work</a>',
                    "Error ./collections/book-slug1.collection.xml:3:1 "
                    "<!-- here",
                    "No link ./media/something.jpg <-- here",
                )
                update_args["error_message"] = "\n".join(lines)
            elif status_id == 5:
                update_args["artifact_urls"] = [
                    {
                        "slug": job["books"][0]["slug"],
                        "url": "https://example.com/",
                    }
                ]
            to_update.append(
                client.put(
                    f"http://localhost/api/jobs/{job_id}", json=update_args
                )
            )
        for response in await asyncio.gather(*to_update):
            response.raise_for_status()
            print("Job updated!")


if __name__ == "__main__":
    asyncio.run(main())
