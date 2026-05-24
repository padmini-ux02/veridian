import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import {
  Shield, LayoutDashboard, ScanLine, History, MessageCircle,
  Flag, User, BarChart3, Users, FileText, LogOut, Sun, Moon, Menu, X
} from 'lucide-react';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const mainNav = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/scan', icon: ScanLine, label: 'Scanner' },
    { to: '/history', icon: History, label: 'History' },
    { to: '/chat', icon: MessageCircle, label: 'AI Assistant' },
    { to: '/reports', icon: Flag, label: 'Reports' },
    { to: '/profile', icon: User, label: 'Profile' },
  ];

  const adminNav = [
    { to: '/admin', icon: BarChart3, label: 'Analytics' },
    { to: '/admin/reports', icon: FileText, label: 'Review Reports' },
    { to: '/admin/users', icon: Users, label: 'Users' },
  ];

  return (
    <div className="shell">
      {open && <div onClick={() => setOpen(false)} style={{ position:'fixed',inset:0,background:'rgba(0,0,0,.6)',zIndex:45 }} />}

      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-mark"><Shield size={17} color="#fff" /></div>
          <div className="brand-name">Veri<span>dian</span></div>
        </div>

        <nav className="nav">
          {mainNav.map(n => (
            <NavLink key={n.to} to={n.to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`} onClick={() => setOpen(false)}>
              <n.icon size={16} />{n.label}
            </NavLink>
          ))}

          {user?.role === 'admin' && (
            <>
              <div className="nav-group-label">Admin</div>
              {adminNav.map(n => (
                <NavLink key={n.to} to={n.to} end className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`} onClick={() => setOpen(false)}>
                  <n.icon size={16} />{n.label}
                </NavLink>
              ))}
            </>
          )}
        </nav>

        <div className="sidebar-bottom">
          <button className="nav-item" onClick={() => { logout(); navigate('/login'); }}>
            <LogOut size={16} /> Sign Out
          </button>
        </div>
      </aside>

      <div className="content">
        <header className="topbar">
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>
            <button className="icon-btn" style={{ display:'none' }} id="mobile-menu" onClick={() => setOpen(!open)}>
              {open ? <X size={18}/> : <Menu size={18}/>}
            </button>
            <span className="topbar-title">{user?.full_name?.split(' ')[0]}'s Workspace</span>
          </div>
          <div className="topbar-right">
            <button className="icon-btn" onClick={toggleTheme} title="Toggle theme">
              {theme === 'dark' ? <Sun size={16}/> : <Moon size={16}/>}
            </button>
            <div style={{ display:'flex', alignItems:'center', gap:8, padding:'4px 10px', background:'var(--bg-2)', borderRadius:'var(--r-sm)', border:'1px solid var(--border)' }}>
              <div className="avatar">{user?.full_name?.[0]?.toUpperCase()}</div>
              <div>
                <div style={{ fontSize:'.8rem', fontWeight:600, lineHeight:1.2 }}>{user?.username}</div>
                <div style={{ fontSize:'.68rem', color:'var(--text-3)', lineHeight:1 }}>{user?.role}</div>
              </div>
            </div>
          </div>
        </header>
        <main><Outlet /></main>
      </div>

      <style>{`#mobile-menu { display: flex; } @media(min-width:769px){ #mobile-menu { display: none !important; } }`}</style>
    </div>
  );
};

export default Layout;
