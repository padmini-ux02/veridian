import React, { useEffect, useState } from 'react';
import { scanAPI } from '../services/api';
import { ScanHistory as HistoryType } from '../types';
import { ShieldCheck, ShieldAlert, ChevronLeft, ChevronRight, Terminal, Search } from 'lucide-react';

const ScanHistory: React.FC = () => {
  const [history, setHistory] = useState<HistoryType | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState('');

  const fetchH = async () => {
    setLoading(true);
    try {
      const r = await scanAPI.getHistory(page, 15, filter || undefined);
      setHistory(r.data);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  useEffect(() => { fetchH(); }, [page, filter]);

  return (
    <div className="page-wrap animate">
      <div className="page-head" style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <div>
          <h1>Scan Log</h1>
          <p>Complete history of your AI fraud analysis</p>
        </div>
        <div className="tabs">
          {['', 'sms', 'email', 'url'].map(f => (
            <button key={f} className={`tab ${filter===f?'active':''}`} onClick={() => { setFilter(f); setPage(1); }}>
              {f ? f.toUpperCase() : 'ALL'}
            </button>
          ))}
        </div>
      </div>

      <div className="panel">
        {loading ? <div className="spin"/> : history?.scans.length === 0 ? (
          <div style={{ padding:60, textAlign:'center', color:'var(--text-3)' }}>
            <Search size={32} style={{ opacity:.3, margin:'0 auto 12px' }}/>
            <div style={{ fontSize:'.9rem' }}>No {filter.toUpperCase()} scans found</div>
          </div>
        ) : (
          <div style={{ overflowX:'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Vector</th>
                  <th>Analyzed Content</th>
                  <th>Result</th>
                  <th>Score</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {history?.scans.map(s => (
                  <tr key={s.id}>
                    <td><span className="badge badge-neutral" style={{ fontSize:'.65rem' }}>{s.scan_type}</span></td>
                    <td>
                      <div className="t-overflow" style={{ fontFamily:'monospace', fontSize:'.8rem', color:'var(--text-2)' }}>{s.input_content}</div>
                    </td>
                    <td>
                      {s.is_fraud ? <span className="badge badge-red"><ShieldAlert size={10}/> FRAUD</span> : <span className="badge badge-green"><ShieldCheck size={10}/> SAFE</span>}
                    </td>
                    <td>
                      <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                        <span style={{ fontWeight:600, fontSize:'.85rem', width:24 }}>{s.risk_score.toFixed(0)}</span>
                        <div className="risk-bar" style={{ width:50, height:4 }}><div className={`risk-bar-fill ${s.risk_category}`} style={{ width:`${s.risk_score}%` }}></div></div>
                      </div>
                    </td>
                    <td style={{ color:'var(--text-3)', fontSize:'.8rem' }}>{new Date(s.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {history && history.total_pages > 1 && (
          <div style={{ padding:'12px 20px', borderTop:'1px solid var(--border)', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <span style={{ fontSize:'.8rem', color:'var(--text-3)' }}>
              Showing <strong style={{ color:'var(--text-2)' }}>{(history.page - 1) * history.page_size + 1}—{Math.min(history.page * history.page_size, history.total)}</strong> of {history.total}
            </span>
            <div style={{ display:'flex', gap:8 }}>
              <button className="btn btn-ghost btn-icon" disabled={page===1} onClick={()=>setPage(p=>p-1)}><ChevronLeft size={16}/></button>
              <button className="btn btn-ghost btn-icon" disabled={page===history.total_pages} onClick={()=>setPage(p=>p+1)}><ChevronRight size={16}/></button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScanHistory;
