import React, { useState, useEffect } from 'react';
import { reportAPI } from '../services/api';
import { Report } from '../types';
import { Flag, Send, Clock, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

const ReportPage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  const [form, setForm] = useState({ type: 'sms', title: '', content: '', description: '', source: '' });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchReports = async () => {
    try {
      const res = await reportAPI.getMyReports(1);
      setReports(res.data.reports);
    } catch (err) { console.error(err); } 
    finally { setLoading(false); }
  };

  useEffect(() => { fetchReports(); }, []);

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setSubmitting(true); setError(''); setSuccess('');
    try {
      await reportAPI.create({ report_type: form.type, title: form.title, content: form.content, description: form.description, source: form.source });
      setSuccess('Report submitted securely. Our threat intelligence team is reviewing it.');
      setShowForm(false); setForm({ type: 'sms', title: '', content: '', description: '', source: '' });
      fetchReports();
    } catch (err: any) { setError(err.response?.data?.detail || 'Submission failed'); }
    finally { setSubmitting(false); }
  };

  const statusMap: Record<string, { label: string, color: string, icon: any }> = {
    pending: { label: 'Pending', color: 'badge-neutral', icon: Clock },
    reviewing: { label: 'Reviewing', color: 'badge-blue', icon: AlertCircle },
    confirmed_fraud: { label: 'Confirmed', color: 'badge-red', icon: CheckCircle2 },
    dismissed: { label: 'Dismissed', color: 'badge-green', icon: XCircle }
  };

  return (
    <div className="page-wrap animate">
      <div className="page-head" style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div>
          <h1>Submit Report</h1>
          <p>Help improve our detection by reporting suspicious content</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <Flag size={15}/> {showForm ? 'Cancel Report' : 'Report Fraud'}
        </button>
      </div>

      {success && <div className="alert alert-success">{success}</div>}

      {showForm && (
        <div className="panel animate" style={{ marginBottom:24, border:'1px solid var(--accent)' }}>
          <div className="panel-body">
            <h2 style={{ fontSize:'1.1rem', marginBottom:20, display:'flex', alignItems:'center', gap:8 }}>
              <Flag size={16} color="var(--accent)"/> New Fraud Report
            </h2>
            {error && <div className="alert alert-error">{error}</div>}
            
            <form onSubmit={handleSubmit}>
              <div className="input-group input-group-2 field">
                <div>
                  <label>Type of Content</label>
                  <select className="input" value={form.type} onChange={set('type')}>
                    <option value="sms">SMS / Text Message</option>
                    <option value="email">Email</option>
                    <option value="url">URL / Website</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label>Short Title</label>
                  <input className="input" required placeholder="e.g., Fake PayPal Login Link" value={form.title} onChange={set('title')}/>
                </div>
              </div>

              <div className="field">
                <label>Exact Content</label>
                <textarea className="input" required placeholder="Paste the exact message or URL..." style={{ minHeight:100, resize:'vertical' }} value={form.content} onChange={set('content')}/>
              </div>

              <div className="field">
                <label>Additional Context (Optional)</label>
                <textarea className="input" placeholder="Why do you think this is fraud? Any other details?" style={{ minHeight:60, resize:'vertical' }} value={form.description} onChange={set('description')}/>
              </div>

              <div className="field">
                <label>Source / Sender (Optional)</label>
                <input className="input" placeholder="Phone number, email, or social handle" value={form.source} onChange={set('source')}/>
              </div>

              <div style={{ display:'flex', justifyContent:'flex-end', gap:10, marginTop:24 }}>
                <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? 'Submitting…' : <><Send size={15}/> Submit Report</>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="panel">
        <div className="panel-body" style={{ borderBottom:'1px solid var(--border)', padding:'16px 20px' }}>
          <div style={{ fontWeight:600 }}>My Submissions</div>
        </div>
        
        {loading ? <div className="spin"/> : reports.length === 0 ? (
          <div style={{ padding:'60px 20px', textAlign:'center', color:'var(--text-3)' }}>
            <Flag size={32} style={{ opacity:0.3, margin:'0 auto 12px' }}/>
            <div style={{ fontSize:'.9rem' }}>No reports submitted yet</div>
          </div>
        ) : (
          <div style={{ overflowX:'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Admin Notes</th>
                </tr>
              </thead>
              <tbody>
                {reports.map(r => {
                  const st = statusMap[r.status] || { label: r.status, color:'badge-neutral', icon:Clock };
                  const Icon = st.icon;
                  return (
                    <tr key={r.id}>
                      <td style={{ fontWeight:500 }}>{r.title}</td>
                      <td><span style={{ fontSize:'.7rem', fontWeight:700, textTransform:'uppercase', color:'var(--text-3)' }}>{r.report_type}</span></td>
                      <td><span className={`badge ${st.color}`}><Icon size={12}/>{st.label}</span></td>
                      <td style={{ color:'var(--text-2)' }}>{new Date(r.created_at).toLocaleDateString()}</td>
                      <td>
                        {r.admin_notes ? <span className="t-overflow" style={{ fontSize:'.8rem', color:'var(--text-2)' }} title={r.admin_notes}>{r.admin_notes}</span> : <span style={{ color:'var(--border-2)' }}>—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportPage;
