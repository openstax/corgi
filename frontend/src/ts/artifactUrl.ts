export function isSafeArtifactUrl(
  value: string | null | undefined,
): value is string {
  if (value == null) return false;
  if (!/^https?:\/\/[^/?#\\\s]+(?:[/?#]|$)/i.test(value)) return false;

  try {
    const url = new URL(value);
    return (
      (url.protocol === "http:" || url.protocol === "https:") &&
      Boolean(url.hostname) &&
      !url.username &&
      !url.password
    );
  } catch {
    return false;
  }
}
