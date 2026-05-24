import React, { useEffect, useState, useRef } from 'react';
import { chatAPI } from '../services/api';
import { ChatMessage } from '../types';
import { Send, Bot, Sparkles } from 'lucide-react';

const SUGGESTED = [
  'How do I spot a phishing email?',
  'What should I do if I clicked a suspicious link?',
  'How do scammers fake caller ID?',
  'Is this SMS message dangerous?',
];

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role:'assistant', content:"Hello! I'm Veridian's security assistant. I can help you understand fraud tactics, analyze suspicious content, and advise on what steps to take. What's on your mind?" }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior:'smooth' }); }, [messages, loading]);

  const send = async (msg: string) => {
    if (!msg.trim() || loading) return;
    setInput('');
    setMessages(p => [...p, { role:'user', content:msg }]);
    setLoading(true);
    try {
      const r = await chatAPI.send(msg);
      setMessages(p => [...p, { role:'assistant', content:r.data.response }]);
    } catch {
      setMessages(p => [...p, { role:'assistant', content:'I\'m having trouble connecting right now. Please try again in a moment.' }]);
    } finally { setLoading(false); }
  };

  const handleSubmit = (e: React.FormEvent) => { e.preventDefault(); send(input); };

  return (
    <div className="page-wrap animate" style={{ maxWidth:800 }}>
      <div className="page-head">
        <h1>AI Assistant</h1>
        <p>Ask anything about fraud detection, phishing, or security</p>
      </div>

      <div style={{ background:'var(--bg-1)', border:'1px solid var(--border)', borderRadius:'var(--r-lg)', overflow:'hidden', display:'flex', flexDirection:'column', height:'calc(100vh - 210px)' }}>
        {/* Header */}
        <div style={{ display:'flex', alignItems:'center', gap:10, padding:'14px 18px', borderBottom:'1px solid var(--border)', background:'var(--bg-2)' }}>
          <div style={{ width:36, height:36, borderRadius:10, background:'linear-gradient(135deg,var(--accent),var(--accent-2))', display:'flex', alignItems:'center', justifyContent:'center' }}>
            <Bot size={20} color="#fff"/>
          </div>
          <div>
            <div style={{ fontWeight:600, fontSize:'.9rem' }}>Security Assistant</div>
            <div style={{ fontSize:'.72rem', color:'var(--green)', display:'flex', alignItems:'center', gap:4 }}>
              <div style={{ width:6, height:6, borderRadius:'50%', background:'var(--green)' }}></div> Online
            </div>
          </div>
          <div style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:4, fontSize:'.72rem', color:'var(--text-3)' }}>
            <Sparkles size={12}/> Powered by Veridian
          </div>
        </div>

        {/* Messages */}
        <div className="chat-body">
          {messages.map((m, i) => (
            <div key={i} className={`chat-msg ${m.role === 'user' ? 'user' : 'bot'}`}>
              <div className={`chat-avatar`} style={{ background: m.role === 'user' ? 'var(--bg-3)' : 'linear-gradient(135deg,var(--accent),var(--accent-2))' }}>
                {m.role === 'user' ? '👤' : <Bot size={14} color="#fff"/>}
              </div>
              <div>
                <div style={{ fontSize:'.7rem', color:'var(--text-3)', marginBottom:4, textAlign: m.role === 'user' ? 'right' : 'left' }}>
                  {m.role === 'user' ? 'You' : 'AI Assistant'}
                </div>
                <div className="chat-bubble">
                  {m.content.split('\n').map((line, j) => <span key={j}>{line}<br/></span>)}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-msg bot">
              <div className="chat-avatar" style={{ background:'linear-gradient(135deg,var(--accent),var(--accent-2))' }}>
                <Bot size={14} color="#fff"/>
              </div>
              <div>
                <div style={{ fontSize:'.7rem', color:'var(--text-3)', marginBottom:4 }}>AI Assistant</div>
                <div className="chat-bubble" style={{ padding:'14px 18px' }}>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={endRef}/>
        </div>

        {/* Suggested */}
        {messages.length === 1 && (
          <div style={{ padding:'8px 18px', display:'flex', gap:6, flexWrap:'wrap', borderTop:'1px solid var(--border)' }}>
            {SUGGESTED.map((q,i) => (
              <button key={i} onClick={() => send(q)} className="btn btn-ghost btn-sm" style={{ borderRadius:20, fontSize:'.75rem' }}>{q}</button>
            ))}
          </div>
        )}

        {/* Input */}
        <form onSubmit={handleSubmit} className="chat-input-row">
          <input
            className="input"
            style={{ flex:1, borderRadius:20 }}
            placeholder="Ask about fraud, phishing, or security…"
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="btn btn-primary btn-icon" style={{ borderRadius:'50%', flexShrink:0 }} disabled={!input.trim() || loading}>
            <Send size={16}/>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPage;
