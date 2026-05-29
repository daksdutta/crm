import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import KanbanBoard from "./pages/KanbanBoard";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<KanbanBoard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;