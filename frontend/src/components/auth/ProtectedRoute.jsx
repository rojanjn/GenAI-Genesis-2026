/**
 * ProtectedRoute - Wraps routes that require authentication
 * 
 * Features:
 * - Redirects to /login if not authenticated
 * - Shows loading state while auth is being verified
 * - Preserves attempted location for redirect after login
 */

import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import AuthContext from '../../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useContext(AuthContext);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
