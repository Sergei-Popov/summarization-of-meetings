import { Flex, Typography } from "antd";

import { ProductRoutes } from "./ProductRoutes";

export function App() {
  return (
    <Flex component="main" vertical gap="large" align="center">
      <Typography.Title>Meeting App</Typography.Title>
      <ProductRoutes />
    </Flex>
  );
}
