import { Alert, Skeleton, Typography } from "antd";
import { useEffect, useState } from "react";

import { loadHealth, type HealthResponse } from "../../api/client";

type ViewState =
  | { kind: "loading" }
  | { kind: "ready"; health: HealthResponse }
  | { kind: "failed" };

export function HealthPanel() {
  const [state, setState] = useState<ViewState>({ kind: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    void loadHealth(controller.signal)
      .then((health) => setState({ kind: "ready", health }))
      .catch(() => {
        if (!controller.signal.aborted) {
          setState({ kind: "failed" });
        }
      });
    return () => controller.abort();
  }, []);

  if (state.kind === "loading") {
    return <Skeleton active paragraph={{ rows: 1 }} title={false} />;
  }
  if (state.kind === "failed") {
    return (
      <Alert
        type="error"
        showIcon
        title="Приложение не готово"
        description="Проверьте локальное хранилище и повторите запуск."
      />
    );
  }
  return (
    <Alert
      type="success"
      showIcon
      title="Локальное приложение готово"
      description={
        <Typography.Text>
          Версия {state.health.version}; проверено {state.health.timestamp}
        </Typography.Text>
      }
    />
  );
}
