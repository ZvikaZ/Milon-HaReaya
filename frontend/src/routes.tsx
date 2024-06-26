import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { MainLayout } from "./pages/main-layout.tsx";

const AppRoutes = () => {
  return (
    <Router basename="/Milon-HaReaya">
      <Routes>
        <Route path="/" element={<MainLayout />} />
        <Route path="/:type" element={<MainLayout />} />
        <Route path="/:type/:id" element={<MainLayout />} />
        <Route path="*" element={<MainLayout />} />
      </Routes>
    </Router>
  );
};

export { AppRoutes };
