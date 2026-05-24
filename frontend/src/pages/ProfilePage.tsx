import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { User, Mail, Phone, Lock, CheckCircle2, Shield } from 'lucide-react';

const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  
  const [form, setForm] = useState({ name: user?.full_name || '', phone: user?.phone || '' });
  const [pw, setPw] = useState({ current: '', new: '', confirm: '' });
  
  const [pLoad, setPLoad] = useState(false);
  const [pwLoad, setPwLoad] = useState(false);
  const [pMsg, setPMsg] = useState({ type: '', text: '' });
  const [pwMsg, setPwMsg] = useState({ type: '', text: '' });

  const handleProfile = async (e: React.FormEvent) => {
    e.preventDefault(); setPMsg({ type: '', text: '' }); setPLoad(true);
    try {
      const r = await authAPI.updateProfile({ full_name: form.name, phone: form.phone });
      updateUser(r.data);
      setPMsg({ type: 'success', text: 'Profile updated' });
    } catch (err: any) { setPMsg({ type: 'error', text: err.response?.data?.detail || 'Update failed' }); }
    finally { setPLoad(false); }
  };

  const handlePw = async (e: React.FormEvent) => {
    e.preventDefault(); setPwMsg({ type: '', text: '' });
    if (pw.new !== pw.confirm) return setPwMsg({ type: 'error', text: 'Passwords do not match' });
    setPwLoad(true);
    try {
      await authAPI.changePassword({ current_password: pw.current, new_password: pw.new });
      setPwMsg({ type: 'success', text: 'Password changed securely' });
      setPw({ current: '', new: '', confirm: '' });
    } catch (err: any) { setPwMsg({ type: 'error', text: err.response?.data?.detail || 'Change failed' }); }
    finally { setPwLoad(false); }
  };

  return (
    <div className="page-wrap animate" style={{ maxWidth: 900 }}>
      <div className="page-head">
        <h1>Account Settings</h1>
        <p>Manage your profile and security preferences</p>
      </div>

      <div className="panel" style={{ marginBottom:24, display:'flex', alignItems:'center', gap:24, padding:24 }}>
        <div style={{ width:72, height:72, borderRadius:20, background:'linear-gradient(135deg,var(--accent),var(--accent-2))', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'2rem', fontWeight:800, color:'#fff', flexShrink:0 }}>
          {user?.full_name?.[0]?.toUpperCase()}
        </div>
        <div style={{ flex:1 }}>
          <h2 style={{ fontSize:'1.4rem', fontWeight:700, letterSpacing:'-.3px' }}>{user?.full_name}</h2>
          <div style={{ display:'flex', gap:16, color:'var(--text-3)', fontSize:'.85rem', marginTop:4 }}>
            <span style={{ display:'flex', alignItems:'center', gap:4 }}><Mail size={14}/> {user?.email}</span>
            <span style={{ display:'flex', alignItems:'center', gap:4 }}><User size={14}/> @{user?.username}</span>
          </div>
          <div style={{ marginTop:10, display:'flex', gap:8 }}>
            <span className={`badge ${user?.role === 'admin' ? 'badge-purple' : 'badge-blue'}`}><Shield size={12}/>{user?.role}</span>
            <span className="badge badge-green"><CheckCircle2 size={12}/>Active</span>
          </div>
        </div>
        <div style={{ textAlign:'right', color:'var(--text-3)', fontSize:'.8rem' }}>
          <div>Joined</div>
          <div style={{ fontWeight:600, color:'var(--text-2)', marginTop:2 }}>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}</div>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24 }}>
        <div className="panel">
          <div className="panel-body" style={{ borderBottom:'1px solid var(--border)' }}>
            <div style={{ fontWeight:600, display:'flex', alignItems:'center', gap:8 }}><User size={16} color="var(--accent)"/> Profile Information</div>
          </div>
          <div className="panel-body">
            {pMsg.text && <div className={`alert alert-${pMsg.type}`} style={{ marginBottom:16 }}>{pMsg.text}</div>}
            <form onSubmit={handleProfile}>
              <div className="field">
                <label>Full Name</label>
                <input className="input" required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/>
              </div>
              <div className="field">
                <label>Email Address</label>
                <input className="input" disabled value={user?.email || ''} style={{ opacity:0.5 }}/>
              </div>
              <div className="field">
                <label>Phone Number</label>
                <div className="input-icon">
                  <Phone size={15}/>
                  <input className="input" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})} placeholder="+1 234 567 8900"/>
                </div>
              </div>
              <button type="submit" className="btn btn-primary btn-block" style={{ marginTop:8 }} disabled={pLoad}>{pLoad ? 'Saving…' : 'Save Changes'}</button>
            </form>
          </div>
        </div>

        <div className="panel">
          <div className="panel-body" style={{ borderBottom:'1px solid var(--border)' }}>
            <div style={{ fontWeight:600, display:'flex', alignItems:'center', gap:8 }}><Lock size={16} color="var(--accent)"/> Security</div>
          </div>
          <div className="panel-body">
            {pwMsg.text && <div className={`alert alert-${pwMsg.type}`} style={{ marginBottom:16 }}>{pwMsg.text}</div>}
            <form onSubmit={handlePw}>
              <div className="field">
                <label>Current Password</label>
                <input className="input" type="password" required value={pw.current} onChange={e=>setPw({...pw,current:e.target.value})}/>
              </div>
              <div className="field">
                <label>New Password</label>
                <input className="input" type="password" required value={pw.new} onChange={e=>setPw({...pw,new:e.target.value})}/>
              </div>
              <div className="field">
                <label>Confirm Password</label>
                <input className="input" type="password" required value={pw.confirm} onChange={e=>setPw({...pw,confirm:e.target.value})}/>
              </div>
              <div style={{ fontSize:'.75rem', color:'var(--text-3)', marginBottom:16 }}>Must be 8+ chars with uppercase, lowercase, number, and symbol.</div>
              <button type="submit" className="btn btn-primary btn-block" disabled={pwLoad}>{pwLoad ? 'Updating…' : 'Update Password'}</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
