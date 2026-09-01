import { App as AntApp, ConfigProvider, theme } from "antd";
import ruRU from "antd/locale/ru_RU";
import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app/App";

function ThemedApp() {
  const [mediaQuery] = useState(() => window.matchMedia("(prefers-color-scheme: dark)"));
  const [dark, setDark] = useState(mediaQuery.matches);

  useEffect(() => {
    const updateTheme = (event: MediaQueryListEvent) => setDark(event.matches);
    mediaQuery.addEventListener("change", updateTheme);
    return () => mediaQuery.removeEventListener("change", updateTheme);
  }, [mediaQuery]);

  return (
    <ConfigProvider
      locale={ruRU}
      theme={{ algorithm: dark ? theme.darkAlgorithm : theme.defaultAlgorithm }}
    >
      <AntApp>
        <App />
      </AntApp>
    </ConfigProvider>
  );
}

const root = document.getElementById("root");
if (root === null) {
  throw new Error("root element is missing");
}

createRoot(root).render(
  <StrictMode>
    <ThemedApp />
  </StrictMode>,
);
