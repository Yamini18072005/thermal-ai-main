import { useState } from 'react';

export default function AuthGateway({ onLoginSuccess, apiUrl }) {
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const cleanApiUrl = (apiUrl || '').replace(/\/+$/, '');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!email.trim() || !password.trim()) {
      setErrorMessage('Please provide both email and password.');
      return;
    }

    if (authMode === 'register') {
      if (!name.trim()) {
        setErrorMessage('Please enter your full name.');
        return;
      }
      if (password.length < 6) {
        setErrorMessage('Password must be at least 6 characters long.');
        return;
      }
      if (password !== confirmPassword) {
        setErrorMessage('Passwords do not match. Please re-enter.');
        return;
      }
    }

    if (!cleanApiUrl) {
      setErrorMessage('Unable to connect to server. Please configure VITE_API_URL.');
      return;
    }

    setLoading(true);

    const endpoint = authMode === 'login'
      ? `${cleanApiUrl}/api/auth/login`
      : `${cleanApiUrl}/api/auth/register`;

    const payload = authMode === 'login'
      ? { email: email.trim(), password }
      : { name: name.trim(), email: email.trim(), password };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      let data;
      try {
        data = await response.json();
      } catch {
        data = { detail: response.statusText };
      }

      if (response.ok && data.access_token) {
        setSuccessMessage(
          authMode === 'login'
            ? '✓ Authentication verified. Accessing Command Center...'
            : '✓ Municipal Analyst account registered successfully in MongoDB Atlas!'
        );
        setTimeout(() => {
          onLoginSuccess(data.access_token, data.user);
        }, 600);
      } else {
        if (response.status === 401) {
          setErrorMessage(data.detail || 'Invalid email or password. Please check your credentials.');
        } else if (response.status === 400) {
          setErrorMessage(data.detail || 'An account with this email already exists.');
        } else if (response.status === 404) {
          setErrorMessage('Authentication service is unavailable. Please try again later.');
        } else if (response.status === 503) {
          setErrorMessage('Authentication database is unavailable. Please try again later.');
        } else if (response.status === 422) {
          setErrorMessage('Invalid input format. Password must be at least 6 characters and email must be valid.');
        } else {
          setErrorMessage(data.detail || 'Authentication failed. Please verify your details.');
        }
      }
    } catch {
      setErrorMessage('Unable to connect to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-master-wrapper" style={{
      minHeight: '100vh',
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      background: 'var(--bg-deep-navy, #060A17)',
      padding: '1.5rem',
      overflow: 'hidden'
    }}>
      {/* Ambient Layered Background */}
      <div className="ambient-bg-layer">
        <div className="bg-thermal-glow" />
        <div className="bg-cyan-glow" />
        <div className="bg-city-grid" />
      </div>

      {/* Main Authentication Card */}
      <div style={{
        position: 'relative',
        zIndex: 10,
        width: '100%',
        maxWidth: '490px',
        background: 'rgba(13, 22, 44, 0.94)',
        backdropFilter: 'blur(24px)',
        borderRadius: '20px',
        border: '1px solid rgba(0, 242, 254, 0.3)',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.6), 0 0 35px rgba(0, 242, 254, 0.15)',
        padding: '2.5rem 2.2rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.4rem',
      }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, rgba(255, 85, 0, 0.25) 0%, rgba(0, 242, 254, 0.25) 100%)',
            border: '1px solid var(--border-cyber, rgba(0, 242, 254, 0.4))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.8rem',
            boxShadow: '0 0 20px rgba(0, 242, 254, 0.2)'
          }}>
            🔥
          </div>

          <div>
            <h1 style={{
              fontFamily: 'var(--font-title, "Outfit", sans-serif)',
              fontSize: '1.75rem',
              fontWeight: 900,
              color: '#FFF',
              letterSpacing: '0.5px',
              lineHeight: 1.2,
              margin: 0,
            }}>
              THERMAL EQUITY <span style={{ color: 'var(--color-cyan, #00F2FE)' }}>AI</span>
            </h1>
            <p style={{
              fontSize: '0.82rem',
              color: '#94A3B8',
              marginTop: '0.25rem',
              marginBottom: 0,
              fontFamily: 'var(--font-body, "Plus Jakarta Sans", sans-serif)'
            }}>
              Chennai Urban Climate Intelligence & Decision Command
            </p>
          </div>

          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.45rem',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            padding: '0.25rem 0.75rem',
            borderRadius: '100px',
            fontSize: '0.72rem',
            fontWeight: 800,
            color: '#10B981',
            letterSpacing: '0.5px',
            fontFamily: 'var(--font-mono, monospace)'
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: '#10B981',
              display: 'inline-block',
              boxShadow: '0 0 8px #10B981'
            }} />
            FASTAPI & MONGODB ATLAS AUTHENTICATION
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          background: 'rgba(6, 11, 25, 0.8)',
          borderRadius: '12px',
          padding: '4px',
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <button
            type="button"
            onClick={() => { setAuthMode('login'); setErrorMessage(''); setSuccessMessage(''); }}
            style={{
              padding: '0.65rem',
              borderRadius: '9px',
              border: 'none',
              background: authMode === 'login' ? 'linear-gradient(90deg, #00F2FE 0%, #3B82F6 100%)' : 'transparent',
              color: authMode === 'login' ? '#060A17' : '#94A3B8',
              fontFamily: 'var(--font-title, sans-serif)',
              fontSize: '0.88rem',
              fontWeight: 800,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: authMode === 'login' ? '0 0 15px rgba(0, 242, 254, 0.35)' : 'none'
            }}
          >
            SIGN IN
          </button>
          <button
            type="button"
            onClick={() => { setAuthMode('register'); setErrorMessage(''); setSuccessMessage(''); }}
            style={{
              padding: '0.65rem',
              borderRadius: '9px',
              border: 'none',
              background: authMode === 'register' ? 'linear-gradient(90deg, #00F2FE 0%, #3B82F6 100%)' : 'transparent',
              color: authMode === 'register' ? '#060A17' : '#94A3B8',
              fontFamily: 'var(--font-title, sans-serif)',
              fontSize: '0.88rem',
              fontWeight: 800,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: authMode === 'register' ? '0 0 15px rgba(0, 242, 254, 0.35)' : 'none'
            }}
          >
            CREATE ACCOUNT
          </button>
        </div>

        {/* Error Alert Box */}
        {errorMessage && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.18)',
            border: '1px solid rgba(239, 68, 68, 0.5)',
            borderRadius: '10px',
            padding: '0.75rem 1rem',
            color: '#FCA5A5',
            fontSize: '0.82rem',
            lineHeight: 1.4,
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.5rem',
          }}>
            <span style={{ fontSize: '1rem', lineHeight: 1 }}>⚠</span>
            <span style={{ flex: 1 }}>{errorMessage}</span>
          </div>
        )}

        {/* Success Alert Box */}
        {successMessage && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.18)',
            border: '1px solid rgba(16, 185, 129, 0.5)',
            borderRadius: '10px',
            padding: '0.75rem 1rem',
            color: '#6EE7B7',
            fontSize: '0.82rem',
            lineHeight: 1.4,
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>{successMessage}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {authMode === 'register' && (
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#CBD5E1', marginBottom: '0.35rem', letterSpacing: '0.5px' }}>
                FULL NAME
              </label>
              <input
                type="text"
                placeholder="e.g., Dr. Ananya Sundaram"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{
                  width: '100%',
                  background: 'rgba(6, 11, 25, 0.85)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  borderRadius: '10px',
                  padding: '0.75rem 1rem',
                  color: '#FFF',
                  fontSize: '0.9rem',
                  fontFamily: 'var(--font-body, sans-serif)',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#00F2FE'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'}
              />
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#CBD5E1', marginBottom: '0.35rem', letterSpacing: '0.5px' }}>
              OFFICIAL EMAIL ADDRESS
            </label>
            <input
              type="email"
              placeholder="officer@chennaicorporation.gov.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: '100%',
                background: 'rgba(6, 11, 25, 0.85)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '10px',
                padding: '0.75rem 1rem',
                color: '#FFF',
                fontSize: '0.9rem',
                fontFamily: 'var(--font-body, sans-serif)',
                outline: 'none',
                transition: 'border-color 0.2s',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#00F2FE'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#CBD5E1', marginBottom: '0.35rem', letterSpacing: '0.5px' }}>
              PASSWORD {authMode === 'register' && <span style={{ color: '#64748B', fontWeight: 400 }}>(min 6 chars)</span>}
            </label>
            <div style={{ position: 'relative' }}>
              <input
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                background: 'rgba(6, 11, 25, 0.85)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                borderRadius: '10px',
                padding: '0.75rem 1rem',
                color: '#FFF',
                fontSize: '0.9rem',
                fontFamily: 'var(--font-body, sans-serif)',
                outline: 'none',
                transition: 'border-color 0.2s',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#00F2FE'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'}
              />
              <button
                type="button"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                style={{ position: 'absolute', right: '0.7rem', top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'transparent', color: '#94A3B8', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 700 }}
              >
                {showPassword ? 'HIDE' : 'SHOW'}
              </button>
            </div>
          </div>

          {authMode === 'register' && (
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 800, color: '#CBD5E1', marginBottom: '0.35rem', letterSpacing: '0.5px' }}>
                CONFIRM PASSWORD
              </label>
              <div style={{ position: 'relative' }}>
                <input
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="••••••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  background: 'rgba(6, 11, 25, 0.85)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  borderRadius: '10px',
                  padding: '0.75rem 1rem',
                  color: '#FFF',
                  fontSize: '0.9rem',
                  fontFamily: 'var(--font-body, sans-serif)',
                  outline: 'none',
                  transition: 'border-color 0.2s',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#00F2FE'}
                onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.12)'}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((visible) => !visible)}
                  aria-label={showConfirmPassword ? 'Hide password confirmation' : 'Show password confirmation'}
                  style={{ position: 'absolute', right: '0.7rem', top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'transparent', color: '#94A3B8', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 700 }}
                >
                  {showConfirmPassword ? 'HIDE' : 'SHOW'}
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: '0.5rem',
              width: '100%',
              padding: '0.85rem',
              borderRadius: '10px',
              border: 'none',
              background: 'linear-gradient(90deg, #00F2FE 0%, #0088FF 100%)',
              color: '#060A17',
              fontFamily: 'var(--font-title, sans-serif)',
              fontSize: '0.95rem',
              fontWeight: 900,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
              boxShadow: '0 0 25px rgba(0, 242, 254, 0.4)',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}
          >
            {loading ? (
              <span>VERIFYING SECURE CREDENTIALS...</span>
            ) : (
              <span>{authMode === 'login' ? 'SIGN IN TO COMMAND CENTER' : 'REGISTER MUNICIPAL ACCOUNT'} →</span>
            )}
          </button>
        </form>

      </div>
    </div>
  );
}
