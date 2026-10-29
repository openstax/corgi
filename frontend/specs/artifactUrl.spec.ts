import { describe, expect, it } from "@jest/globals";
import { isSafeArtifactUrl } from "../src/ts/artifactUrl";

const artifactUrlCases = {
  accepted_by_both: [
    {
      name: "HTTPS artifact URL",
      url: "https://example.com/artifacts/build-1.zip",
    },
    {
      name: "HTTP URL with a non-default port",
      url: "http://example.com:8080/artifacts/build-1.zip",
    },
    {
      name: "uppercase scheme",
      url: "HTTPS://example.com/artifacts/build-1.zip",
    },
    {
      name: "valid percent escape in the authority",
      url: "https://example%2ecom/artifacts/build-1.zip",
    },
    {
      name: "malformed percent escapes outside the authority",
      url: "https://example.com/artifacts/%zz.zip?download=%xx",
    },
  ],
  rejected_by_both: [
    {
      name: "script URL",
      url: "javascript:alert(1)",
    },
    {
      name: "data URL",
      url: "data:text/html,<script>alert(1)</script>",
    },
    {
      name: "unsupported scheme",
      url: "ftp://example.com/artifacts/build-1.zip",
    },
    {
      name: "protocol-relative URL",
      url: "//example.com/artifacts/build-1.zip",
    },
    {
      name: "relative URL",
      url: "/artifacts/build-1.zip",
    },
    {
      name: "missing authority",
      url: "https:///artifacts/build-1.zip",
    },
    {
      name: "whitespace in authority",
      url: "https://bad host.example/artifact.zip",
    },
    {
      name: "malformed percent escape in authority",
      url: "https://example.com%zz/artifact.zip",
    },
    {
      name: "backslash in authority",
      url: "https://example.com\\evil/artifact.zip",
    },
    {
      name: "backslash instead of scheme slashes",
      url: "https:\\example.com/artifacts/build-1.zip",
    },
    {
      name: "empty userinfo",
      url: "https://@example.com/artifacts/build-1.zip",
    },
    {
      name: "credentials",
      url: "https://user:password@example.com/artifacts/build-1.zip",
    },
    {
      name: "non-numeric port",
      url: "https://example.com:invalid/artifact.zip",
    },
    {
      name: "port above the valid range",
      url: "https://example.com:65536/artifact.zip",
    },
    {
      name: "leading whitespace",
      url: " https://example.com/artifacts/build-1.zip",
    },
    {
      name: "trailing newline",
      url: "https://example.com/artifacts/build-1.zip\n",
    },
  ],
  known_parser_differences: [
    {
      name: "WHATWG URL rejects an out-of-range numeric IPv4 host; urlsplit accepts it as a nonempty hostname",
      url: "https://256.0.0.1/artifact.zip",
      frontend_accepts: false,
      backend_accepts: true,
    },
  ],
  optional_value_differences: [
    {
      name: "null is treated as missing by the backend",
      url: null,
      frontend_accepts: false,
      backend_passes_through: true,
    },
    {
      name: "empty string is treated as missing by the backend",
      url: "",
      frontend_accepts: false,
      backend_passes_through: true,
    },
  ],
};

describe("isSafeArtifactUrl", () => {
  it.each(artifactUrlCases.accepted_by_both)(
    "accepts shared case: $name",
    ({ url }) => {
      expect(isSafeArtifactUrl(url)).toBe(true);
    },
  );

  it.each(artifactUrlCases.rejected_by_both)(
    "rejects shared case: $name",
    ({ url }) => {
      expect(isSafeArtifactUrl(url)).toBe(false);
    },
  );

  it.each(artifactUrlCases.known_parser_differences)(
    "documents parser difference: $name",
    ({ url, frontend_accepts }) => {
      expect(isSafeArtifactUrl(url)).toBe(frontend_accepts);
    },
  );

  it.each(artifactUrlCases.optional_value_differences)(
    "documents optional-value difference: $name",
    ({ url, frontend_accepts }) => {
      expect(isSafeArtifactUrl(url)).toBe(frontend_accepts);
    },
  );

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
    "https://bad host.example/artifact.zip",
    "https://%zz/artifact.zip",
    "https://example.com\\evil/artifact.zip",
    "https:\\example.com/artifacts/build-1.zip",
    "https://user:password@example.com/artifacts/build-1.zip",
    "https://example.com:invalid/artifacts/build-1.zip",
  ])("rejects unsafe or malformed URL %s", (url) => {
    expect(isSafeArtifactUrl(url)).toBe(false);
  });
});
