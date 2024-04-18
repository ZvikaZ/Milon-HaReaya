import "@mantine/core/styles.css";

import { MantineProvider } from "@mantine/core";
import { MainLayout } from "./main-layout.tsx";

export default function App() {
  return (
    <MantineProvider>
      <MainLayout />
    </MantineProvider>
  );
}
