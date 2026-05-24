import React, { useEffect, useState } from 'react';
import { adminAPI } from '../services/api';
import { Report } from '../types';
import { Flag, Clock, AlertCircle, CheckCircle2, XCircle, ChevronLeft, ChevronRight, Edit2 } from 'lucide-react';

const AdminReports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filter, setFilter] = useState('');
  const [edit, setEdit] = useState<string | null>(null);
  const [eStat, setEStat] = useState('');
  const [eNote, setENote] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchR = async () => {
    setLoading(true);
    try {
      const r = await adminAPI.getReports(page, filter || undefined);
      setReports(r.data.reports); setTotalPages(r.data.total_pages);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  useEffect(() => { fetchR(); }, [page, filter]);

  const handleUpdate = async (id: string) => {
    setSaving(true);
    try {
      await adminAPI.updateReport(id, { status: eStat, admin_notes: eNote });
      setEdit(null); fetchR();
    } catch (err) { console.error(err); } finally { setSaving(false); }
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
          <h1>Triage Reports</h1>
          <p>Review user-submitted fraud reports</p>
        </div>
        <div className="tabs">
          {['', 'pending', 'reviewing', 'confirmed_fraud', 'dismissed'].map(f => (
            <button key={f} className={`tab ${filter===f?'active':''}`} onClick={() => { setFilter(f); setPage(1); }}>
              {f ? f.replace('_',' ').replace(/\b\w/g, c=>c.toUpperCase()) : 'All'}
            </button>
          ))}
        </div>
      </div>

      <div className="panel">
        {loading ? <div className="spin"/> : reports.length === 0 ? (
          <div style={{ padding:60, textAlign:'center', color:'var(--text-3)' }}><Flag size={32} style={{ opacity:.3, margin:'0 auto 12px' }}/>No reports found</div>
        ) : (
          <div style={{ overflowX:'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {reports.map(r => {
                  const st = statusMap[r.status];
                  const Icon = st.icon;
                  return (
                    <React.Fragment key={r.id}>
                      <tr>
                        <td style={{ color:'var(--text-2)' }}>@{r.reporter_username}</td>
                        <td style={{ fontWeight:500 }}>{r.title}</td>
                        <td><span className={`badge ${st.color}`}><Icon size={12}/>{st.label}</span></td>
                        <td style={{ color:'var(--text-3)' }}>{new Date(r.created_at).toLocaleDateString()}</td>
                        <td>
                          <button className="btn btn-ghost btn-sm" onClick={() => { setEdit(edit===r.id ? null : r.id); setEStat(r.status); setENote(r.admin_notes || ''); }}>
                            <Edit2 size={12}/> {edit===r.id ? 'Cancel' : 'Review'}
                          </button>
                        </td>
                      </tr>
                      {edit === r.id && (
                        <tr>
                          <td colSpan={5} style={{ background:'var(--bg-2)', padding:20 }}>
                            <div style={{ background:'var(--bg-1)', padding:16, borderRadius:'var(--r-sm)', border:'1px solid var(--border)', marginBottom:16 }}>
                              <div style={{ fontSize:'.7rem', fontWeight:600, color:'var(--text-3)', textTransform:'uppercase', marginBottom:6 }}>Reported Content</div>
                              <div style={{ fontSize:'.875rem', fontFamily:'monospace', whiteSpace:'pre-wrap' }}>{r.content}</div>
                              {r.description && <div style={{ marginTop:12, fontSize:'.85rem', color:'var(--text-2)' }}><strong>Context:</strong> {r.description}</div>}
                            </div>
                            <div style={{ display:'flex', gap:16, alignItems:'flex-end' }}>
                              <div style={{ flex:1 }}>
                                <label style={{ display:'block', fontSize:'.7rem', fontWeight:600, color:'var(--text-3)', textTransform:'uppercase', marginBottom:6 }}>Update Status</label>
                                <select className="input" value={eStat} onChange={e=>setEStat(e.target.value)}>
                                  <option value="pending">Pending</option>
                                  <option value="reviewing">Reviewing</option>
                                  <option value="confirmed_fraud">Confirmed Fraud</option>
                                  <option value="dismissed">Dismissed</option>
                                </select>
                              </div>
                              <div style={{ flex:2 }}>
                                <label style={{ display:'block', fontSize:'.7rem', fontWeight:600, color:'var(--text-3)', textTransform:'uppercase', marginBottom:6 }}>Admin Notes</label>
                                <input className="input" placeholder="Visible to the user..." value={eNote} onChange={e=>setENote(e.target.value)}/>
                              </div>
                              <button className="btn btn-primary" onClick={() => handleUpdate(r.id)} disabled={saving}>{saving ? 'Saving…' : 'Save Changes'}</button>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        
        {totalPages > 1 && (
          <div style={{ padding:'12px 20px', borderTop:'1px solid var(--border)', display:'flex', justifyContent:'flex-end', gap:8 }}>
            <button className="btn btn-ghost btn-icon" disabled={page===1} onClick={()=>setPage(p=>p-1)}><ChevronLeft size={16}/></button>
            <span style={{ padding:'0 8px', display:'flex', alignItems:'center', fontSize:'.85rem', color:'var(--text-2)' }}>{page} / {totalPages}</span>
            <button className="btn btn-ghost btn-icon" disabled={page===totalPages} onClick={()=>setPage(p=>p+1)}><ChevronRight size={16}/></button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminReports;
