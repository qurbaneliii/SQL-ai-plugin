export function formatDuration(ms?: number | null) {
  if (ms === undefined || ms === null) {
    return "n/a";
  }
  return `${ms} ms`;
}

export function formatValue(value: unknown) {
  if (value === null || value === undefined) {
    return "";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return String(value);
}

export function compactDatabaseUrl(value?: string | null) {
  if (!value) {
    return "Not configured";
  }
  return value.length > 52 ? `${value.slice(0, 28)}...${value.slice(-18)}` : value;
}
