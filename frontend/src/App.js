import './App.css';
import Index from './components/Index';
import AdminDashBoard from './dashboard/AdminDashboard';
import HomePage from './pages/Home';
import Login from './pages/Login';
import Registration from './pages/Registration';
import { BrowserRouter, Route, Routes } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<Registration />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard/*" element={<Index />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
