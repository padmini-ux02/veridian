import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { scanAPI } from '../services/api';
import { ScanStats } from '../types';
import { ArrowRight, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<ScanStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    scanAPI.getStats().then(r => setStats(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="spin" />;

  const pct = (n: number, d: number) => d ? Math.round((n / d) * 100) : 0;
  const fraudRate = pct(stats?.fraud_detected ?? 0, stats?.total_scans ?? 0);

  return (
    <div className="page-wrap animate">
      <div className="page-head">
        <h1>Overview</h1>
        <p>Your fraud detection activity at a glance</p>
      </div>

      <div className="stat-grid" style={{ marginBottom:20 }}>
        <div className="stat-tile">
          <div className="t-label">Total Scans</div>
          <div className="t-value t-purple">{stats?.total_scans ?? 0}</div>
          <div className="t-sub">All time</div>
        </div>
        <div className="stat-tile">
          <div className="t-label">Fraud Detected</div>
          <div className="t-value t-red">{stats?.fraud_detected ?? 0}</div>
          <div className="t-sub">{fraudRate}% fraud rate</div>
        </div>
        <div className="stat-tile">
          <div className="t-label">Safe Content</div>
          <div className="t-value t-green">{stats?.safe_detected ?? 0}</div>
          <div className="t-sub">{100 - fraudRate}% clean</div>
        </div>
        <div className="stat-tile">
          <div className="t-label">Avg Risk Score</div>
          <div className="t-value t-yellow">{(stats?.average_risk_score ?? 0).toFixed(1)}</div>
          <div className="t-sub">Out of 100</div>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 320px', gap:14 }}>
        <div className="panel">
          <div className="panel-body" style={{ borderBottom:'1px solid var(--border)', paddingBottom:14 }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
              <div>
                <div style={{ fontWeight:600, fontSize:'.95rem' }}>Detection Activity</div>
                <div style={{ fontSize:'.78rem', color:'var(--text-3)' }}>Last 30 days</div>
              </div>
              <div style={{ display:'flex', gap:16, fontSize:'.78rem', color:'var(--text-2)' }}>
                <span style={{ display:'flex', alignItems:'center', gap:5 }}><span style={{ width:8, height:8, borderRadius:'50%', background:'var(--accent-2)', display:'inline-block' }}></span>Scans</span>
                <span style={{ display:'flex', alignItems:'center', gap:5 }}><span style={{ width:8, height:8, borderRadius:'50%', background:'var(--red)', display:'inline-block' }}></span>Fraud</span>
              </div>
            </div>
          </div>
          <div className="panel-body" style={{ paddingTop:12 }}>
            {(stats?.scans_by_date?.length ?? 0) > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={stats!.scans_by_date} margin={{ top:5, right:5, left:-20, bottom:0 }}>
                  <defs>
                    <linearGradient id="ga" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.2}/><stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="gb" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.15}/><stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false}/>
                  <XAxis dataKey="date" stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false}/>
                  <YAxis stroke="var(--text-3)" fontSize={11} tickLine={false} axisLine={false}/>
                  <Tooltip contentStyle={{ background:'var(--bg-2)', border:'1px solid var(--border)', borderRadius:8, fontSize:12 }}/>
                  <Area type="monotone" dataKey="total" name="Scans" stroke="#a855f7" strokeWidth={1.5} fill="url(#ga)"/>
                  <Area type="monotone" dataKey="fraud" name="Fraud" stroke="#ef4444" strokeWidth={1.5} fill="url(#gb)"/>
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ height:220, display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-3)', fontSize:'.875rem' }}>
                No scan data yet — <Link to="/scan" style={{ marginLeft:5 }}>run your first scan</Link>
              </div>
            )}
          </div>
        </div>

        <div style={{ display:'flex', flexDirection:'column', gap:14 }}>
          <div className="panel panel-body">
            <div style={{ fontWeight:600, marginBottom:16, fontSize:'.9rem' }}>Breakdown</div>
            {[
              { label:'SMS', value: stats?.sms_scans ?? 0, color:'var(--blue)' },
              { label:'Email', value: stats?.email_scans ?? 0, color:'var(--accent-2)' },
              { label:'URL', value: stats?.url_scans ?? 0, color:'var(--green)' },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ marginBottom:14 }}>
                <div style={{ display:'flex', justifyContent:'space-between', fontSize:'.82rem', marginBottom:5 }}>
                  <span style={{ color:'var(--text-2)' }}>{label}</span>
                  <span style={{ fontWeight:600 }}>{value}</span>
                </div>
                <div className="risk-bar">
                  <div style={{ height:'100%', borderRadius:2, width:`${pct(value, stats?.total_scans ?? 1)}%`, background:color, transition:'width .6s' }}></div>
                </div>
              </div>
            ))}
          </div>

          <div className="panel panel-body" style={{ background:'linear-gradient(135deg, #1a0a3d, #0d1a3d)', border:'1px solid rgba(168,85,247,.15)' }}>
            <div style={{ fontWeight:700, color:'#fff', marginBottom:6 }}>Run a Scan</div>
            <div style={{ fontSize:'.82rem', color:'rgba(255,255,255,.5)', marginBottom:16, lineHeight:1.5 }}>
              Analyze suspicious messages, emails or links instantly.
            </div>
            <Link to="/scan" className="btn btn-primary btn-sm" style={{ gap:6 }}>
              Open Scanner <ArrowRight size={14}/>
            </Link>
          </div>

          <div className="panel panel-body">
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8 }}>
              <span style={{ fontSize:'.82rem', fontWeight:600 }}>Risk Level</span>
              {fraudRate > 30 ? <TrendingUp size={15} color="var(--red)"/> : fraudRate > 10 ? <Minus size={15} color="var(--yellow)"/> : <TrendingDown size={15} color="var(--green)"/>}
            </div>
            <div style={{ fontSize:'2rem', fontWeight:800, color: fraudRate > 30 ? 'var(--red)' : fraudRate > 10 ? 'var(--yellow)' : 'var(--green)', letterSpacing:'-.5px' }}>{fraudRate}%</div>
            <div style={{ fontSize:'.75rem', color:'var(--text-3)', marginTop:2 }}>fraud rate overall</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
