const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");
const express = require("express");

const app = express();
const repoPath = "/corgi";
const corgiRepo = "https://github.com/openstax/corgi";
const frontendRepoDir = path.join(repoPath, "frontend");
const frontendDir = "/app";

function sh(cmd, ignoreExitCode = false) {
  return new Promise((resolve, reject) => {
    exec(cmd, (error, stdout, stderr) => {
      if (!ignoreExitCode && error != null && error.code !== 0) {
        reject(new Error(stderr));
      } else {
        resolve({ error, stdout, stderr });
      }
    });
  });
}

function scopedGit(cmd, kwargs = {}) {
  const { scope = repoPath, ignoreExitCode = false } = kwargs;
  return sh(`git -C ${scope} ${cmd}`, ignoreExitCode);
}

async function isPullable(ref) {
  return (await scopedGit('show-ref'))
    .stdout
    .trim()
    .split('\n')
    .filter(line => line.includes('refs/heads/') || line.includes('refs/remotes/'))
    .some(line => line.endsWith(ref))
}

function gitInit() {
  if (!fs.existsSync(repoPath)) {
    fs.mkdirSync(repoPath, { recursive: true });
    return sh(`git -C ${path.dirname(repoPath)} clone ${corgiRepo}`);
  }
  return Promise.resolve();
}

function copyDirectory(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// Enable JSON request body decoding
app.use(express.json());

app.post("/checkout", async (req, res) => {
  const { ref } = req.body;
  if (ref == null) {
    res.status(500).send("Need commit to checkout");
  } else {
    try {
      await scopedGit("fetch");
      await scopedGit(`checkout ${ref}`);
      if (await isPullable(ref)) {
        await scopedGit("pull --rebase");
      }
      copyDirectory(frontendRepoDir, frontendDir);
      res.sendStatus(200);
    } catch (err) {
      console.error(err);
      res.sendStatus(500);
    }
  }
});

const PORT = process.env.PORT || 3000;
gitInit().catch((err) => {
  throw err;
});
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
