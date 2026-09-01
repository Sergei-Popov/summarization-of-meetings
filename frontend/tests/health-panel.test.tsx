import { act, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadHealth } from "../src/api/client";
import { HealthPanel } from "../src/features/health/HealthPanel";

vi.mock("../src/api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../src/api/client")>();
  return { ...actual, loadHealth: vi.fn() };
});

const mockedLoadHealth = vi.mocked(loadHealth);

describe("HealthPanel", () => {
  beforeEach(() => {
    mockedLoadHealth.mockReset();
  });

  it("renders the ready state returned by the real client boundary", async () => {
    mockedLoadHealth.mockResolvedValue({
      status: "ready",
      version: "0.1.0",
      timestamp: "2026-09-01T12:00:00Z",
    });

    render(<HealthPanel />);

    expect(await screen.findByText("Локальное приложение готово")).toBeInTheDocument();
    expect(screen.getByText(/Версия 0\.1\.0/)).toBeInTheDocument();
  });

  it("renders a safe error state when health loading fails", async () => {
    let rejectHealth: (reason: Error) => void = () => undefined;
    mockedLoadHealth.mockImplementation(
      () =>
        new Promise((_resolve, reject) => {
          rejectHealth = reject;
        }),
    );

    render(<HealthPanel />);
    act(() => rejectHealth(new Error("application.not_ready")));

    expect(await screen.findByText("Приложение не готово")).toBeInTheDocument();
    expect(screen.getByText(/Проверьте локальное хранилище/)).toBeInTheDocument();
  });
});
