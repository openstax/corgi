export function isSafeArtifactUrl(
  value: string | null | undefined,
): value is string {
  if (value == null || value !== value.trim()) return false;
  for (let i = 0; i < value.length; i++) {
    if (value.charCodeAt(i) < 0x20) {
      return false;
    }
  }
  const authority = /^https?:\/\/([^/?#\\\s@]+)(?:[/?#]|$)/i.exec(value);
  if (!authority || /%(?![0-9a-fA-F]{2})/.test(authority[1])) return false;

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
