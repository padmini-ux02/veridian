import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Mail, Lock, CheckCircle } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handle = async (e: React.FormEvent) => {
    e.preventDefault(); setError(''); setLoading(true);
    try { await login(email, password); navigate('/dashboard'); }
    catch (err: any) { setError(err.response?.data?.detail || 'Invalid email or password'); }
    finally { setLoading(false); }
  };

  const features = ['Real-time SMS fraud detection','Phishing URL analysis','AI-powered email scanning','Explainable risk scores'];

  return (
    <div className="auth-shell">
      <div className="auth-left">
        <div className="auth-brand animate">
          <div className="auth-brand-icon">
            <Shield size={38} color="#fff" />
          </div>
          <h1>Veridian</h1>
          <p>Enterprise-grade fraud detection powered by machine learning and NLP</p>

          <div style={{ marginTop:36, textAlign:'left', display:'flex', flexDirection:'column', gap:10 }}>
            {features.map((f,i) => (
              <div key={i} style={{ display:'flex', alignItems:'center', gap:10, color:'rgba(255,255,255,.7)', fontSize:'.875rem' }}>
                <CheckCircle size={15} color="#a855f7" style={{ flexShrink:0 }} /> {f}
              </div>
            ))}
          </div>

          <div className="auth-stats">
            {[['99.2%','Accuracy'],['<50ms','Response'],['3 Types','Supported']].map(([n,l],i) => (
              <div key={i} className="auth-stat">
                <span className="num">{n}</span>
                <span className="lbl">{l}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-form-wrap animate">
          <h2 className="auth-form-title">Welcome back</h2>
          <p className="auth-form-sub">Sign in to your Veridian account</p>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handle}>
            <div className="field">
              <label>Email</label>
              <div className="input-icon">
                <Mail size={15} />
                <input className="input" type="email" required placeholder="you@example.com" value={email} onChange={e => setEmail(e.target.value)} />
              </div>
            </div>
            <div className="field">
              <label>Password</label>
              <div className="input-icon">
                <Lock size={15} />
                <input className="input" type="password" required placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} />
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-block btn-lg" style={{ marginTop:8 }} disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <div className="auth-footer-link">
            No account? <Link to="/register">Create one free</Link>
          </div>

          <div style={{ marginTop:20, padding:'12px 14px', background:'var(--bg-2)', borderRadius:'var(--r-sm)', fontSize:'.78rem', color:'var(--text-3)', border:'1px solid var(--border)' }}>
            <strong style={{ color:'var(--text-2)' }}>Demo Admin:</strong> admin@veridian.io / Admin@123456
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
