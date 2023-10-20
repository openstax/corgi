import os
from datetime import datetime
from shutil import copytree, ignore_patterns
from subprocess import run, PIPE
from shlex import split
from typing import Optional
from enum import Enum
from time import time
import re
import json

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx


server = FastAPI(title="CORGI Hotdog")


class StatusType(str, Enum):
    running = "running"
    building = "building"


class Head(BaseModel):
    corgi_ref: Optional[str]
    enki_ref: Optional[str]
    corgi_modified: Optional[float]
    enki_modified: Optional[float]


class Status(BaseModel):
    enki_status: StatusType


class Bundle(BaseModel):
    head: Head
    status: Status

    def update(
        self, head: Optional[Head] = None, status: Optional[Status] = None
    ):
        return Bundle(
            head=head if head is not None else self.head,
            status=status if status is not None else self.status,
        )

    @staticmethod
    def default():
        return Bundle(
            head=Head(
                corgi_ref="main",
                enki_ref="main",
                corgi_modified=time(),
                enki_modified=time(),
            ),
            status=Status(enki_status=StatusType.running),
        )


class BundleManager:
    __slots__ = ("_bundle", "_bundle_path")

    def __init__(self, bundle_path: str):
        self._bundle: Optional[Bundle] = None
        self._bundle_path = bundle_path

    def _save(self, bundle: Bundle):
        with open(self._bundle_path, "w") as fout:
            fout.write(bundle.json())
        self._bundle = bundle

    def save(
        self, head: Optional[Head] = None, status: Optional[Status] = None
    ):
        self._save(self.bundle.update(head, status))

    @property
    def bundle(self) -> Bundle:
        if self._bundle is not None:
            return self._bundle

        bundle = Bundle.default()
        try:
            default_keys = Bundle.__fields__.keys()
            with open(self._bundle_path) as fin:
                saved = json.load(fin)
            bundle = bundle.update(
                **{k: v for k, v in saved.items() if k in default_keys}
            )
        except Exception:
            self._save(bundle)

        return bundle


# NOTE: These global variables will not work if multiple instances are running
CORGI_REPO = os.environ["CORGI_REPO"]
FRONTEND_PORT = os.environ["HOTDOG_FRONTEND_PORT"]
FRONTEND_HOTDOG = f"http://frontend:{FRONTEND_PORT}/checkout"
REPO_PATH = "/corgi"
BACKEND_REPO_DIR = os.path.join(REPO_PATH, "backend", "app")
BACKEND_DIR = "/app"
REF_REGEX = re.compile(r"^[a-zA-Z0-9_./-]+$")
BUNDLE_PATH = os.environ["BUNDLE_PATH"]
BUNDLE_MGR = BundleManager(BUNDLE_PATH)
HTML_TEMPLATE = (Path(__file__).parent / "index.html.template").read_text()


def sh(cmd: str, ignore_exitcode=False):
    p = run(split(cmd), stdout=PIPE, stderr=PIPE)
    if not ignore_exitcode and p.returncode != 0:
        raise Exception(p.stderr.decode())
    return (p, p.stdout.decode(), p.stderr.decode())


def scoped_git(cmd, scope=REPO_PATH, ignore_exitcode=False):
    return sh(f"git -C {scope} {cmd}", ignore_exitcode)


def is_pullable(ref):
    return any(
        line.endswith(ref)
        for line in scoped_git("show-ref")[1].strip().splitlines()
        if "refs/heads/" in line or "refs/remotes" in line
    )


def _corgi_checkout(ref):
    scoped_git("fetch")
    scoped_git(f"checkout {ref}")
    if is_pullable(ref):
        scoped_git("pull --rebase")
    copytree(
        BACKEND_REPO_DIR,
        BACKEND_DIR,
        dirs_exist_ok=True,
        ignore=ignore_patterns("hotdog*"),
    )
    response = httpx.post(FRONTEND_HOTDOG, json={"ref": ref})
    response.raise_for_status()


@server.post("/checkout")
def corgi_checkout(checkout_request: Head):
    saved = BUNDLE_MGR.bundle.head
    corgi_ref = saved.corgi_ref
    enki_ref = saved.enki_ref
    corgi_modified = saved.corgi_modified
    enki_modified = saved.enki_modified
    if checkout_request.corgi_ref:
        if not REF_REGEX.match(checkout_request.corgi_ref):
            raise Exception("Unsupported ref")
        try:
            _corgi_checkout(checkout_request.corgi_ref)
            corgi_ref = checkout_request.corgi_ref
            corgi_modified = time()
        except Exception:
            _corgi_checkout(saved.corgi_ref)
            raise
    if checkout_request.enki_ref:
        if not REF_REGEX.match(checkout_request.enki_ref):
            raise Exception("Unsupported ref")
        enki_ref = checkout_request.enki_ref
        enki_modified = time()
    BUNDLE_MGR.save(
        head=Head(
            corgi_ref=corgi_ref,
            corgi_modified=corgi_modified,
            enki_ref=enki_ref,
            enki_modified=enki_modified,
        )
    )


@server.get("/head", response_model=Head)
def head():
    return BUNDLE_MGR.bundle.head


@server.get("/")
def home():
    saved = BUNDLE_MGR.bundle.head
    return HTMLResponse(
        f"""\
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORGI Hotdog</title>
</head>
<body>
    <h1>CORGI Hotdog</h1>
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
            const response = await fetch("/hotdog/checkout", {
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
