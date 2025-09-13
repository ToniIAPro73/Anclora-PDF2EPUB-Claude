import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from './AuthContext';

const RegisterForm: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(username, password);
      navigate('/login');
    } catch (err) {
      setError('Registro fallido');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 flex flex-col gap-2">
      <h2>Crear cuenta</h2>
      {error && <p className="text-red-500">{error}</p>}
      <input
        type="text"
        placeholder="Usuario"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="border p-2"
      />
      <input
        type="password"
        placeholder="Contraseña"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="border p-2"
      />
      <button type="submit" className="bg-green-500 text-white p-2">Registrarse</button>
      <p>
        ¿Ya tienes cuenta? <Link to="/login" className="text-blue-500">Inicia sesión</Link>
      </p>
    </form>
  );
};

export default RegisterForm;

