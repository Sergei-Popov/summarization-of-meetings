import { afterEach, describe, expect, it, vi } from "vitest";

import { HealthClientError, loadHealth } from "../src/api/client";

const ready = {
  status: "ready",
  version: "0.1.0",
  timestamp: "2026-09-01T12:00:00Z",
};

const problem = {
  type: "urn:meeting-app:problem:not-ready",
  title: "Not ready",
  status: 503,
  detail: "Starting",
  instance: "/api/v1/health",
  code: "application.not_ready",
  stage: "startup",
  retryable: true,
};

function response(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": status >= 400 ? "application/problem+json" : "application/json" },
  });
}

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("loadHealth", () => {
  it("calls only the versioned same-origin endpoint and validates success", async () => {
    const fetchMock = vi.fn().mockResolvedValue(response(ready));
    vi.stubGlobal("fetch", fetchMock);

    await expect(loadHealth()).resolves.toEqual(ready);
    expect(fetchMock).toHaveBeenCalledOnce();
    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/v1/health");
    expect(fetchMock.mock.calls[0]?.[1]).toMatchObject({
      headers: { Accept: "application/json, application/problem+json" },
    });
  });

  it("converts a validated RFC 9457 problem to a stable client error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response(problem, 503)));

    await expect(loadHealth()).rejects.toMatchObject({
      code: "application.not_ready",
      status: 503,
    });
  });

  it("rejects responses missing required generated-contract fields", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ status: "ready" })));

    await expect(loadHealth()).rejects.toEqual(
      new HealthClientError("client.invalid_response", 200),
    );
  });

  it("aborts a request after its timeout", async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, options: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          options.signal?.addEventListener("abort", () => reject(new DOMException("", "AbortError")));
        }),
      ),
    );

    const request = loadHealth(undefined, 25).catch((error: unknown) => error);
    await vi.advanceTimersByTimeAsync(25);

    await expect(request).resolves.toMatchObject({ code: "client.timeout" });
  });

  it("propagates caller cancellation as a stable client error", async () => {
    const caller = new AbortController();
    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, options: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          options.signal?.addEventListener("abort", () => reject(new DOMException("", "AbortError")));
        }),
      ),
    );

    const request = loadHealth(caller.signal).catch((error: unknown) => error);
    caller.abort();

    await expect(request).resolves.toMatchObject({ code: "client.cancelled" });
  });
});
