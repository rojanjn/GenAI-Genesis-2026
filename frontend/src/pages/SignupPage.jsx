/**
 * SignupPage - User registration interface
 * 
 * Features:
 * - Email/password/name form
 * - Password strength validation
 * - Error handling and display
 * - Link to login page
 * - Auto-login on successful signup
 */

import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import AuthContext from '../contexts/AuthContext';
import './AuthPages.css';

const SignupPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [loading, setLoading] = useState(false);

  const { signup } = useContext(AuthContext);
  const navigate = useNavigate();

  // Validate password strength
  const validatePassword = (pwd) => {
    if (pwd.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      return false;
    }
    if (!/[A-Z]/.test(pwd)) {
      setPasswordError('Password must contain at least one uppercase letter');
      return false;
    }
    if (!/[a-z]/.test(pwd)) {
      setPasswordError('Password must contain at least one lowercase letter');
      return false;
    }
    if (!/[0-9]/.test(pwd)) {
      setPasswordError('Password must contain at least one number');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const handlePasswordChange = (e) => {
    const pwd = e.target.value;
    setPassword(pwd);
    if (pwd) {
      validatePassword(pwd);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validatePassword(password)) {
      return;
    }

    if (!displayName.trim()) {
      setError('Please enter your name');
      return;
    }

    setLoading(true);

    try {
      await signup(email, password, displayName);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Create Account</h1>
        <p className="auth-subtitle">Start your journaling journey today</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="displayName">Full Name</label>
            <input
              id="displayName"
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="John Doe"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@example.com"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={handlePasswordChange}
              placeholder="••••••••"
              required
              disabled={loading}
            />
            {passwordError && <p className="password-hint error">{passwordError}</p>}
            {password && !passwordError && (
              <p className="password-hint success">Password is strong ✓</p>
            )}
            {!password && (
              <p className="password-hint">
                Must be 8+ characters with uppercase, lowercase, and numbers
              </p>
            )}
          </div>

          <button 
            type="submit" 
            className="auth-button"
            disabled={loading || passwordError !== ''}
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="auth-link">
              Log in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
