import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Register from './pages/Register';
import { useAuth } from './context/AuthContext';
import type { JSX } from 'react';
import { Template } from './components/Template'

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  console.log(user);
  return user && user.verified === true ? children : <Navigate to='/login' replace />;
}


function App() {
  return (
    <div>
      <Template />
      <Routes>
        <Route path='/login' element={<Login />} />
        <Route path='/chat' element={<PrivateRoute><Chat /></PrivateRoute>} />
        <Route path='/' element={<Navigate to='/chat' />} />
        <Route path="*" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </div>
  )
}

// <Route path="*" element={<Login />} />  -> Not found is better

export default App;

