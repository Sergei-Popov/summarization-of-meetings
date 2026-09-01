import type { components } from "./generated/schema";

export type HealthResponse = components["schemas"]["HealthResponse"];
export type ProblemDetails = components["schemas"]["ProblemDetails"];

const HEALTH_ENDPOINT = "/api/v1/health";
const DEFAULT_TIMEOUT_MS = 5_000;

export class HealthClientError extends Error {
  constructor(
    public readonly code: string,
    public readonly status?: number,
  ) {
    super(code);
    this.name = "HealthClientError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isHealthResponse(value: unknown): value is HealthResponse {
  return (
    isRecord(value) &&
    value.status === "ready" &&
    typeof value.version === "string" &&
    value.version.length > 0 &&
    typeof value.timestamp === "string" &&
    value.timestamp.length > 0
  );
}

function isProblemDetails(value: unknown): value is ProblemDetails {
  return (
    isRecord(value) &&
    typeof value.type === "string" &&
    typeof value.title === "string" &&
    typeof value.status === "number" &&
    typeof value.detail === "string" &&
    typeof value.instance === "string" &&
    typeof value.code === "string" &&
    typeof value.stage === "string" &&
    typeof value.retryable === "boolean"
  );
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    throw new HealthClientError("client.invalid_response", response.status);
  }
}

export async function loadHealth(
  signal?: AbortSignal,
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<HealthResponse> {
  if (signal?.aborted === true) {
    throw new HealthClientError("client.cancelled");
  }

  const controller = new AbortController();
  let timedOut = false;
  const cancel = () => controller.abort(signal?.reason);
  signal?.addEventListener("abort", cancel, { once: true });
  const timeout = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    const response = await fetch(HEALTH_ENDPOINT, {
      headers: { Accept: "application/json, application/problem+json" },
      signal: controller.signal,
    });
    const payload = await readJson(response);
    if (!response.ok) {
      if (!isProblemDetails(payload)) {
        throw new HealthClientError("client.invalid_response", response.status);
      }
      throw new HealthClientError(payload.code, response.status);
    }
    if (!isHealthResponse(payload)) {
      throw new HealthClientError("client.invalid_response", response.status);
    }
    return payload;
  } catch (error: unknown) {
    if (error instanceof HealthClientError) {
      throw error;
    }
    if (controller.signal.aborted) {
      throw new HealthClientError(timedOut ? "client.timeout" : "client.cancelled");
    }
    throw new HealthClientError("client.network_error");
  } finally {
    window.clearTimeout(timeout);
    signal?.removeEventListener("abort", cancel);
  }
}
