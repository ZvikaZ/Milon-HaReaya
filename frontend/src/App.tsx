//TODO: linter
//TODO: page route
//TODO: fix mobile layout
//TODO: PWABBuilder (for mobile installation)
//TODO: lighthouse
//TODO: keep in git the mongo functions, for reference
//TODO: give error to http://localhost:5173/Milon-HaReaya/toc/doesnt-exist

import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { AppRoutes } from "./routes.tsx";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <AppRoutes />
      </MantineProvider>{" "}
    </QueryClientProvider>
  );
}
