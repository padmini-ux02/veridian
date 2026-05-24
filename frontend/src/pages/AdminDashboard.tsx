import React, { useEffect, useState } from 'react';
import { adminAPI } from '../services/api';
import { AdminStats } from '../types';
import { Users, Shield, ShieldAlert, Flag, TrendingUp, BarChart3, Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminAPI.getDashboard().then(r => setStats(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spin"/>;

  const pie = [
    { name: 'SMS', value: stats?.sms_scans || 0, color: '#3b82f6' },
    { name: 'Email', value: stats?.email_scans || 0, color: '#a855f7' },
    { name: 'URL', value: stats?.url_scans || 0, color: '#22c55e' },
  ];

  const reportData = [
    { label: 'Pending', val: stats?.reports?.pending || 0, color: 'var(--text-3)', icon: Clock },
    { label: 'Reviewing', val: stats?.reports?.reviewing || 0, color: 'var(--blue)', icon: AlertCircle },
    { label: 'Fraud', val: stats?.reports?.confirmed_fraud || 0, color: 'var(--red)', icon: CheckCircle2 },
    { label: 'Dismissed', val: stats?.reports?.dismissed || 0, color: 'var(--green)', icon: XCircle },
  ];

  return (
    <div className="page-wrap animate">
      <div className="page-head">
        <h1>Platform Overview</h1>
        <p>Global system analytics, active threats, and user activity</p>
      </div>

      <div className="stat-grid" style={{ marginBottom:20 }}>
        <div className="stat-tile">
          <div className="t-label">Total Users</div>
          <div className="t-value t-blue">{stats?.total_users || 0}</div>
          <div className="t-sub"><Users size={12} style={{ display:'inline', marginRight:4 }}/>Registered accounts</div>
        </div>
        <div className="stat-tile">
          <div className="t-label">Global Scans</div>
          <div className="t-value t-purple">{stats?.total_scans || 0}</div>
          <div className="t-sub"><Shield size={12} style={{ display:'inline', marginRight:4 }}/>Items processed</div>
        </div>
        <div className="stat-tile">
          <div className="t-label">Threats Blocked</div>
          <div className="t-value t-red">{stats?.fraud_detected || 0}</div>
          <div className="t-sub"><ShieldAlert size={12} style={{ display:'inline', marginRight:4 }}/>Confirmed fraud</div>
        </div>
        <div className="stat-tile">
          <div className="t-label">Open Reports</div>
          <div className="t-value t-yellow">{stats?.reports?.pending || 0}</div>
          <div className="t-sub"><Flag size={12} style={{ display:'inline', marginRight:4 }}/>Awaiting review</div>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 340px', gap:16, marginBottom:16 }}>
        <div className="panel">
          <div className="panel-body" style={{ borderBottom:'1px solid var(--border)', display:'flex', alignItems:'center', gap:8 }}>
            <TrendingUp size={16} color="var(--accent)"/> <span style={{ fontWeight:600 }}>Threat Timeline (30 Days)</span>
          </div>
          <div className="panel-body" style={{ height:300 }}>
            {(stats?.fraud_trends?.length || 0) > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats!.fraud_trends} margin={{ top:5, right:5, left:-20, bottom:0 }}>
                  <defs>
                    <linearGradient id="ca" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#a855f7" stopOpacity={0.2}/><stop offset="95%" stopColor="#a855f7" stopOpacity={0}/></linearGradient>
                    <linearGradient id="cb" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#ef4444" stopOpacity={0.2}/><stop offset="95%" stopColor="#ef4444" stopOpacity={0}/></linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false}/>
                  <XAxis dataKey="date" stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false}/>
                  <YAxis stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false}/>
                  <Tooltip contentStyle={{ background:'var(--bg-2)', border:'1px solid var(--border)', borderRadius:8, fontSize:12 }}/>
                  <Area type="monotone" dataKey="total" name="Total Activity" stroke="#a855f7" strokeWidth={2} fill="url(#ca)"/>
                  <Area type="monotone" dataKey="fraud" name="Fraud Detected" stroke="#ef4444" strokeWidth={2} fill="url(#cb)"/>
                </AreaChart>
              </ResponsiveContainer>
            ) : <div style={{ height:'100%', display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-3)' }}>No data</div>}
          </div>
        </div>

        <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
          <div className="panel">
            <div className="panel-body" style={{ borderBottom:'1px solid var(--border)', display:'flex', alignItems:'center', gap:8 }}>
              <BarChart3 size={16} color="var(--accent)"/> <span style={{ fontWeight:600 }}>Vector Distribution</span>
            </div>
            <div className="panel-body" style={{ display:'flex', alignItems:'center', gap:20 }}>
              <div style={{ width:100, height:100 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart><Pie data={pie} cx="50%" cy="50%" innerRadius={35} outerRadius={50} paddingAngle={2} dataKey="value">{pie.map((e, i) => <Cell key={i} fill={e.color}/>)}</Pie></PieChart>
                </ResponsiveContainer>
              </div>
              <div style={{ flex:1, display:'flex', flexDirection:'column', gap:8 }}>
                {pie.map((p, i) => (
                  <div key={i} style={{ display:'flex', justifyContent:'space-between', fontSize:'.8rem' }}>
                    <span style={{ display:'flex', alignItems:'center', gap:6 }}><div style={{ width:8, height:8, borderRadius:2, background:p.color }}/>{p.name}</span>
                    <span style={{ fontWeight:600 }}>{p.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-body" style={{ borderBottom:'1px solid var(--border)', display:'flex', alignItems:'center', gap:8 }}>
              <Flag size={16} color="var(--accent)"/> <span style={{ fontWeight:600 }}>Report Triage</span>
            </div>
            <div className="panel-body">
              {reportData.map((r, i) => (
                <div key={i} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'8px 0', borderBottom: i<3 ? '1px solid var(--border)' : 'none' }}>
                  <span style={{ display:'flex', alignItems:'center', gap:8, fontSize:'.8rem', color:'var(--text-2)' }}><r.icon size={14} style={{ color: r.color }}/> {r.label}</span>
                  <span style={{ fontWeight:600 }}>{r.val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-body" style={{ borderBottom:'1px solid var(--border)' }}>
          <div style={{ fontWeight:600 }}>Recent Threat Activity</div>
        </div>
        {stats?.recent_scans?.length === 0 ? (
          <div style={{ padding:40, textAlign:'center', color:'var(--text-3)' }}>No recent scans</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Vector</th>
                <th>Result</th>
                <th>Confidence</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {stats?.recent_scans?.map((s, i) => (
                <tr key={i}>
                  <td><span className="badge badge-neutral">{s.scan_type}</span></td>
                  <td><span className={`badge ${s.risk_category==='low'?'badge-green':s.risk_category==='medium'?'badge-yellow':'badge-red'}`}>{s.risk_category}</span></td>
                  <td style={{ fontWeight:500 }}>{s.fraud_probability.toFixed(1)}%</td>
                  <td style={{ color:'var(--text-3)' }}>{new Date(s.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
