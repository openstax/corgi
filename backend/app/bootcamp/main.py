import os
from datetime import datetime
from shutil import copytree, ignore_patterns
from subprocess import run, PIPE
from typing import Optional
from time import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx


server = FastAPI(title="CORGI Bootcamp")


class Head(BaseModel):
    corgi_ref: Optional[str]
    enki_ref: Optional[str]
    corgi_modified: Optional[float]
    enki_modified: Optional[float]


class Bundle(BaseModel):
    head: Head


# NOTE: These global variables will not work if multiple instances are running
CORGI_REPO = "https://github.com/openstax/corgi"
FRONTEND_BOOTCAMP = "http://frontend:3000/checkout"
REPO_PATH = "/corgi"
BACKEND_REPO_DIR = os.path.join(REPO_PATH, "backend", "app")
BACKEND_DIR = "/app"
saved_bundle = Bundle(
    head=Head(
        corgi_ref="main",
        enki_ref="main",
        corgi_modified=time(),
        enki_modified=time(),
    )
)


def sh(cmd: str, ignore_exitcode=False):
    p = run(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    if not ignore_exitcode and p.returncode != 0:
        raise Exception(p.stderr.decode())
    return (p, p.stdout, p.stderr)


def scoped_git(cmd, scope=REPO_PATH):
    return sh(f"git -C {scope} {cmd}")


def save(*, head: Optional[Head] = None):
    global saved_bundle
    prev = load()
    saved_bundle = Bundle(head=head if head is not None else prev.head)


def load():
    return saved_bundle


def _corgi_checkout(ref):
    scoped_git("fetch")
    scoped_git(f"checkout {ref}")
    scoped_git("pull --rebase")
    copytree(
        BACKEND_REPO_DIR,
        BACKEND_DIR,
        dirs_exist_ok=True,
        ignore=ignore_patterns("bootcamp*"),
    )
    response = httpx.post(FRONTEND_BOOTCAMP, json={"ref": ref})
    response.raise_for_status()


@server.post("/checkout")
def corgi_checkout(checkout_request: Head):
    saved = load().head
    corgi_ref = saved.corgi_ref
    enki_ref = saved.enki_ref
    corgi_modified = saved.corgi_modified
    enki_modified = saved.enki_modified
    if checkout_request.corgi_ref:
        try:
            _corgi_checkout(checkout_request.corgi_ref)
            corgi_ref = checkout_request.corgi_ref
            corgi_modified = time()
        except Exception:
            _corgi_checkout(saved.corgi_ref)
            raise
    if checkout_request.enki_ref:
        enki_ref = checkout_request.enki_ref
        enki_modified = time()
    save(
        head=Head(
            corgi_ref=corgi_ref,
            corgi_modified=corgi_modified,
            enki_ref=enki_ref,
            enki_modified=enki_modified,
        )
    )


@server.get("/head", response_model=Head)
def head():
    return load().head


@server.get("/")
def home():
    saved = load().head
    return HTMLResponse(
        f"""\
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORGI Bootcamp</title>
</head>
<body>
    <h1>CORGI Bootcamp</h1>
    <form id="ref-form">
        <label for="corgi_ref">CORGI Ref:</label>
        <input type="text" id="corgi_ref" name="corgi_ref" placeholder="{saved.corgi_ref}">
        <br>
        <label for="enki_ref">Enki Ref:</label>
        <input type="text" id="enki_ref" name="enki_ref" placeholder="{saved.enki_ref}">
        <br>
        <button id="submit-btn" type="submit">Submit</button>
    </form>
    <div>
        CORGI last modified: {datetime.fromtimestamp(saved.corgi_modified or 0)}
    </div>
    <div>
        Enki last modified: {datetime.fromtimestamp(saved.enki_modified or 0)}
    </div>
"""
        + """\
    <script>
        document.getElementById("ref-form").addEventListener("submit", async (event) => {
            event.preventDefault();

            const formData = new FormData(event.target);
            const data = {};
            const submitBtn = document.getElementById("submit-btn");

            formData.forEach((value, key) => {
                data[key] = value;
            });

            submitBtn.disabled = true;
            const response = await fetch("/bootcamp/checkout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });
            submitBtn.disabled = false;

            if (response.ok) {
                alert("Checkout successful!");
            } else {
                alert("Something bad happened; maybe check the logs");
            }
        });

    </script>
</body>
</html>
"""
    )


if not os.path.exists(REPO_PATH):
    os.makedirs(REPO_PATH)
    sh(f'git -C "{os.path.dirname(REPO_PATH)}" clone "{CORGI_REPO}"')
