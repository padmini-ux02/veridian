import React, { useEffect, useState } from 'react';
import { adminAPI } from '../services/api';
import { User } from '../types';
import { Users, UserCheck, UserX, ChevronLeft, ChevronRight, Shield, Search } from 'lucide-react';

const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [toggling, setToggling] = useState<string | null>(null);

  const fetchU = async () => {
    setLoading(true);
    try {
      const r = await adminAPI.getUsers(page);
      setUsers(r.data.users); setTotalPages(r.data.total_pages);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  useEffect(() => { fetchU(); }, [page]);

  const toggleStatus = async (id: string, active: boolean) => {
    setToggling(id);
    try {
      await adminAPI.toggleUserStatus(id, !active);
      setUsers(p => p.map(u => u.id === id ? { ...u, is_active: !active } : u));
    } catch (err) { console.error(err); } finally { setToggling(null); }
  };

  const filtered = users.filter(u => 
    u.email.toLowerCase().includes(search.toLowerCase()) || 
    u.username.toLowerCase().includes(search.toLowerCase()) || 
    u.full_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page-wrap animate">
      <div className="page-head">
        <h1>Manage Users</h1>
        <p>Review and manage platform access</p>
      </div>

      <div className="panel">
        <div className="panel-body" style={{ padding:'16px 20px', borderBottom:'1px solid var(--border)', display:'flex', gap:16, alignItems:'center' }}>
          <div className="input-icon" style={{ flex:1, maxWidth:400 }}>
            <Search size={15}/>
            <input className="input" placeholder="Search by name, username or email..." value={search} onChange={e=>setSearch(e.target.value)}/>
          </div>
          <div style={{ display:'flex', gap:16, fontSize:'.8rem', color:'var(--text-3)' }}>
            <span style={{ display:'flex', alignItems:'center', gap:4 }}><UserCheck size={14} color="var(--green)"/> Active</span>
            <span style={{ display:'flex', alignItems:'center', gap:4 }}><UserX size={14} color="var(--red)"/> Inactive</span>
          </div>
        </div>

        {loading ? <div className="spin"/> : filtered.length === 0 ? (
          <div style={{ padding:60, textAlign:'center', color:'var(--text-3)' }}><Users size={32} style={{ opacity:.3, margin:'0 auto 12px' }}/>No users found</div>
        ) : (
          <div style={{ overflowX:'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Last Login</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(u => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ display:'flex', alignItems:'center', gap:12 }}>
                        <div style={{ width:32, height:32, borderRadius:'50%', background: u.role==='admin' ? 'linear-gradient(135deg,var(--accent),var(--accent-2))' : 'var(--bg-3)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'.8rem', fontWeight:700, color: u.role==='admin' ? '#fff' : 'var(--text-2)', flexShrink:0 }}>
                          {u.full_name?.[0]?.toUpperCase()}
                        </div>
                        <div>
                          <div style={{ fontWeight:600, fontSize:'.875rem' }}>{u.full_name}</div>
                          <div style={{ fontSize:'.75rem', color:'var(--text-3)' }}>@{u.username} • {u.email}</div>
                        </div>
                      </div>
                    </td>
                    <td><span className={`badge ${u.role==='admin'?'badge-purple':'badge-neutral'}`}><Shield size={10}/>{u.role}</span></td>
                    <td><span className={`badge ${u.is_active?'badge-green':'badge-red'}`}>{u.is_active?'Active':'Inactive'}</span></td>
                    <td style={{ color:'var(--text-2)' }}>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td style={{ color:'var(--text-3)' }}>{u.last_login ? new Date(u.last_login).toLocaleDateString() : '—'}</td>
                    <td>
                      {u.role !== 'admin' && (
                        <button className={`btn btn-sm ${u.is_active?'btn-danger':'btn-success'}`} disabled={toggling===u.id} onClick={()=>toggleStatus(u.id, u.is_active)}>
                          {toggling===u.id ? '…' : u.is_active ? <><UserX size={12}/> Disable</> : <><UserCheck size={12}/> Enable</>}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
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

export default AdminUsers;
