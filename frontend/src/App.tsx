//TODO: linter
//TODO: page route
//TODO: fix mobile layout
//TODO: PWABBuilder (for mobile installation)
//TODO: lighthouse

import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { MainLayout } from "./main-layout.tsx";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <MainLayout />
      </MantineProvider>{" "}
    </QueryClientProvider>
  );
}
