import { RequireAuth } from "./fetch-utils";
import { handleError } from "./utils";
import type { PipelineVersionItem, Version } from "./types";

export async function fetchPipelineVersions(): Promise<PipelineVersionItem[]> {
  try {
    return await (await fetch("/api/pipeline-version/")).json();
  } catch (error) {
    handleError(error);
    return [];
  }
}

export async function fetchVersion(): Promise<Version> {
  try {
    return await (await fetch("/api/version/")).json();
  } catch (error) {
    handleError(error);
    return {};
  }
}

export async function fetchAvailableTags(): Promise<string[]> {
  try {
    const resp = await RequireAuth.fetchJson(
      "/api/version/tags/openstax::enki?count=5",
    );
    return resp.items;
  } catch (error) {
    handleError(error);
    return [];
  }
}

export async function setPipelineVersions(
  versions: PipelineVersionItem[],
): Promise<PipelineVersionItem[]> {
  const handleAuthError = () => {
    throw new Error("You do not have permission to set pipeline versions.");
  };
  const resp = await RequireAuth.sendJson("/api/pipeline-version/", versions, {
    method: "PUT",
    handleAuthError,
  });
  return await resp.json();
}
