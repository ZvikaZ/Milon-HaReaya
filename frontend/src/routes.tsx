import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { NotFound } from "./pages/not-found.tsx";
import { MainLayout } from "./pages/main-layout.tsx";

const AppRoutes = () => {
  return (
    <Router basename="/Milon-HaReaya">
      <Routes>
        <Route path="/" element={<MainLayout />} />
        <Route path="/:type/:id" element={<MainLayout />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
};

export { AppRoutes };
