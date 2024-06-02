import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { MainLayout } from "./main-layout.tsx";

const queryClient = new QueryClient();

console.log('starting. check is:', import.meta.env.VITE_CHECK)

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <MainLayout />
      </MantineProvider>{" "}
    </QueryClientProvider>
  );
}
