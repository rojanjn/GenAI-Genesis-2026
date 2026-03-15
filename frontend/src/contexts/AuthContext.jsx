/**
 * AuthContext - Manages user authentication state across the application
 * 
 * Provides:
 * - user: Current authenticated user object
 * - token: JWT authentication token
 * - loading: Auth state loading status
 * - error: Current auth error message
 * - login: Function to authenticate user
 * - signup: Function to create new account
 * - logout: Function to clear auth state
 */

import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext(null);

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load token from sessionStorage on mount
  useEffect(() => {
    const storedToken = sessionStorage.getItem('auth_token');
    const storedUser = sessionStorage.getItem('auth_user');

    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
      } catch (e) {
        console.error('Failed to parse stored user:', e);
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('auth_user');
      }
    }

    setLoading(false);
  }, []);

  const signup = async (email, password, displayName) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          display_name: displayName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Signup failed');
      }

      const data = await response.json();

      // Store token and user info
      sessionStorage.setItem('auth_token', data.token);
      sessionStorage.setItem('auth_user', JSON.stringify({
        uid: data.user_id,
        email: data.email,
        displayName: data.display_name,
      }));

      setToken(data.token);
      setUser({
        uid: data.user_id,
        email: data.email,
        displayName: data.display_name,
      });

      return data;
    } catch (err) {
      const errorMessage = err.message || 'Signup failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();

      // Store token and user info
      sessionStorage.setItem('auth_token', data.token);
      sessionStorage.setItem('auth_user', JSON.stringify({
        uid: data.user_id,
        email: data.email,
        displayName: data.display_name,
      }));

      setToken(data.token);
      setUser({
        uid: data.user_id,
        email: data.email,
        displayName: data.display_name,
      });

      return data;
    } catch (err) {
      const errorMessage = err.message || 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('auth_user');
    setToken(null);
    setUser(null);
    setError(null);
  };

  const value = {
    user,
    token,
    loading,
    error,
    login,
    signup,
    logout,
    isAuthenticated: !!token,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
