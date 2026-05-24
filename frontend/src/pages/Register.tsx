import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Mail, Lock, User } from 'lucide-react';

const Register: React.FC = () => {
  const [form, setForm] = useState({ email:'', username:'', full_name:'', password:'', confirm:'' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handle = async (e: React.FormEvent) => {
    e.preventDefault(); setError('');
    if (form.password !== form.confirm) return setError('Passwords do not match');
    
    // No client-side password validation constraints

    setLoading(true);
    try {
      await register({ email: form.email, username: form.username, full_name: form.full_name, password: form.password });
      navigate('/dashboard');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setError(Array.isArray(detail) ? detail[0]?.msg : detail || 'Registration failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-shell">
      <div className="auth-left">
        <div className="auth-brand animate">
          <div className="auth-brand-icon">
            <Shield size={38} color="#fff" />
          </div>
          <h1>Veridian</h1>
          <p>Join thousands of users protecting themselves from digital fraud</p>

          <div style={{ marginTop:40, display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, position:'relative', zIndex:1 }}>
            {[
              { num:'2.4M+', desc:'Scans performed' },
              { num:'98.7%', desc:'Threat blocked' },
              { num:'3 sec', desc:'Avg analysis time' },
              { num:'Free', desc:'Always free tier' },
            ].map((s,i) => (
              <div key={i} style={{ background:'rgba(255,255,255,.04)', border:'1px solid rgba(255,255,255,.06)', borderRadius:10, padding:'16px 14px' }}>
                <div style={{ fontSize:'1.4rem', fontWeight:800, color:'#fff' }}>{s.num}</div>
                <div style={{ fontSize:'.75rem', color:'rgba(255,255,255,.4)', marginTop:2 }}>{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-form-wrap animate">
          <h2 className="auth-form-title">Create account</h2>
          <p className="auth-form-sub">Start detecting fraud for free today</p>

          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handle}>
            <div className="field">
              <label>Full Name</label>
              <div className="input-icon">
                <User size={15}/>
                <input className="input" required placeholder="Jane Doe" value={form.full_name} onChange={set('full_name')} />
              </div>
            </div>
            <div className="input-group input-group-2 field">
              <div>
                <label style={{ fontSize:'.75rem', fontWeight:600, color:'var(--text-2)', textTransform:'uppercase', letterSpacing:'.5px', display:'block', marginBottom:6 }}>Username</label>
                <input className="input" required placeholder="janedoe" value={form.username} onChange={set('username')} />
              </div>
              <div>
                <label style={{ fontSize:'.75rem', fontWeight:600, color:'var(--text-2)', textTransform:'uppercase', letterSpacing:'.5px', display:'block', marginBottom:6 }}>Email</label>
                <div className="input-icon" style={{ position:'relative' }}>
                  <Mail size={15}/>
                  <input className="input" type="email" required placeholder="jane@co.com" value={form.email} onChange={set('email')} />
                </div>
              </div>
            </div>
            <div className="input-group input-group-2 field">
              <div>
                <label style={{ fontSize:'.75rem', fontWeight:600, color:'var(--text-2)', textTransform:'uppercase', letterSpacing:'.5px', display:'block', marginBottom:6 }}>Password</label>
                <div className="input-icon" style={{ position:'relative' }}>
                  <Lock size={15}/>
                  <input className="input" type="password" required placeholder="8+ characters" value={form.password} onChange={set('password')} />
                </div>
              </div>
              <div>
                <label style={{ fontSize:'.75rem', fontWeight:600, color:'var(--text-2)', textTransform:'uppercase', letterSpacing:'.5px', display:'block', marginBottom:6 }}>Confirm</label>
                <div className="input-icon" style={{ position:'relative' }}>
                  <Lock size={15}/>
                  <input className="input" type="password" required placeholder="Repeat password" value={form.confirm} onChange={set('confirm')} />
                </div>
              </div>
            </div>
            <div style={{ fontSize:'.75rem', color:'var(--text-3)', marginBottom:16 }}>
              Requires uppercase, lowercase, number and special character
            </div>
            <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={loading}>
              {loading ? 'Creating account…' : 'Create free account'}
            </button>
          </form>

          <div className="auth-footer-link">
            Already have an account? <Link to="/login">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
