import { describe, expect, it } from "@jest/globals";
import { isSafeArtifactUrl } from "../src/ts/artifactUrl";

describe("isSafeArtifactUrl", () => {
  it.each([
    "https://example.com/artifacts/build-1.zip",
    "http://example.com:8080/artifacts/build-1.zip",
  ])("accepts HTTP(S) URL %s", (url) => {
    expect(isSafeArtifactUrl(url)).toBe(true);
  });

  it.each([
    null,
    undefined,
    "",
    "javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "ftp://example.com/artifacts/build-1.zip",
    "//example.com/artifacts/build-1.zip",
    "/artifacts/build-1.zip",
    "https:///artifacts/build-1.zip",
    "https:\\example.com/artifacts/build-1.zip",
    "https://user:password@example.com/artifacts/build-1.zip",
    "https://example.com:invalid/artifacts/build-1.zip",
  ])("rejects unsafe or malformed URL %s", (url) => {
    expect(isSafeArtifactUrl(url)).toBe(false);
  });
});
