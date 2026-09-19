import { useState } from 'react';
import type { User } from '../types/user';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null); // Default to null when no backend

  const login = () => {
    setUser({
      id: '1',
      name: 'Ajay',
      email: 'ajay@example.com'
    });
  };

  const logout = () => {
    setUser(null);
  };

  return { user, login, logout, isAuthenticated: !!user };
};
