import { Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import CreateApp from "./pages/CreateApp";
import EditApp from "./pages/EditApp";
import ViewApp from "./pages/ViewApp";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import UserPage from "./pages/UserPage";
import AdminPortal from "./pages/AdminPortal";
import AgentInstructions from "./pages/AgentInstructions";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/apps/create" element={<CreateApp />} />
      <Route path="/apps/:slug" element={<ViewApp />} />
      <Route path="/apps/:slug/edit" element={<EditApp />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Navigate to="/login?mode=signup" replace />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/users/:username" element={<UserPage />} />
      <Route path="/admin" element={<AdminPortal />} />
      <Route path="/admin/claims" element={<Navigate to="/admin" replace />} />
      <Route path="/agent-instructions" element={<AgentInstructions />} />
    </Routes>
  );
}

export default App;
