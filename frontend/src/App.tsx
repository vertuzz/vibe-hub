import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import CreateDream from "./pages/CreateDream";
import ViewDream from "./pages/ViewDream";
import Login from "./pages/Login";
import Profile from "./pages/Profile";

function App() {
  return (
    <div className="container mx-auto p-4">
      <nav className="mb-8 flex gap-4">
        <a href="/">Home</a>
        <a href="/dreams/create">Create</a>
        <a href="/login">Login</a>
        <a href="/profile">Profile</a>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dreams/create" element={<CreateDream />} />
        <Route path="/dreams/:id" element={<ViewDream />} />
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </div>
  );
}

export default App;
