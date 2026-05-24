import React, { useState, useRef } from 'react';
import { scanAPI } from '../services/api';
import { ScanResult } from '../types';
import { Terminal, Zap, ShieldAlert, ShieldCheck, AlertTriangle, Camera, Upload, X, RefreshCw, Eye } from 'lucide-react';
import Tesseract from 'tesseract.js';

const TYPES = ['sms', 'email', 'url'] as const;

const ScanPage: React.FC = () => {
  const [type, setType] = useState<'sms'|'email'|'url'>('sms');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState('');

  // OCR & Camera Scanner States
  const [cameraActive, setCameraActive] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrProgress, setOcrProgress] = useState('');
  const [cameraError, setCameraError] = useState('');

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startCamera = async () => {
    setCameraError('');
    setCameraActive(true);
    setError('');
    // Wait a brief tick for the video element to mount
    setTimeout(async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: 'environment' } }
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      } catch (err: any) {
        console.error(err);
        setCameraError('Could not access camera. Please verify permission settings, or upload an image file instead.');
      }
    }, 100);
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const closeScanner = () => {
    stopCamera();
    setCameraActive(false);
    setCameraError('');
  };

  const doOCR = async (imageSrc: any) => {
    setOcrLoading(true);
    setOcrProgress('Loading scanning intelligence...');
    setError('');
    try {
      const result = await Tesseract.recognize(imageSrc, 'eng', {
        logger: m => {
          if (m.status === 'recognizing text') {
            setOcrProgress(`Extracting content: ${Math.round(m.progress * 100)}%`);
          }
        }
      });
      
      const text = result.data.text;
      if (text && text.trim()) {
        let cleaned = text.trim();
        if (type === 'url') {
          // Extract first URL if scanning for URL
          const urlMatch = cleaned.match(/(https?:\/\/[^\s⟦⟧]+)/i);
          if (urlMatch) {
            cleaned = urlMatch[0];
          } else {
            // Check if there is a raw domain without HTTP
            const domainMatch = cleaned.match(/([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-z]{2,}(?:\/[^\s]*)?)/i);
            if (domainMatch) {
              cleaned = 'https://' + domainMatch[0];
            }
          }
        }
        setContent(cleaned);
        closeScanner();
      } else {
        setError('No text detected in the image. Please ensure the text is well-lit and clearly readable.');
        closeScanner();
      }
    } catch (err: any) {
      console.error(err);
      setError('OCR extraction failed. Please try again or type manually.');
      closeScanner();
    } finally {
      setOcrLoading(false);
    }
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        stopCamera();
        doOCR(canvas);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      doOCR(file);
    }
  };

  const triggerFileBrowser = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try { const r = await scanAPI.analyze({ scan_type: type, content }); setResult(r.data); }
    catch (err: any) { setError(err.response?.data?.detail || 'Analysis failed'); }
    finally { setLoading(false); }
  };

  const riskColor = (cat: string) => ({ low:'var(--green)', medium:'var(--yellow)', high:'var(--red)', critical:'var(--red)' }[cat] || 'var(--text-2)');
  const riskBadge = (cat: string) => ({ low:'badge-green', medium:'badge-yellow', high:'badge-red', critical:'badge-red' }[cat] || 'badge-neutral');

  const placeholders: Record<string, string> = {
    sms: '> Paste suspicious SMS message here…\n> Or click the Camera button to scan a photo of it!',
    email: '> Paste email body or subject line here…\n> Or click the Camera button to capture email content.',
    url: '> Enter suspicious URL here…\n> Or scan a link through the camera!',
  };

  return (
    <div className="page-wrap animate">
      {/* Dynamic CSS styles for Camera OCR overlay */}
      <style>{`
        .scanner-overlay {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(10, 15, 30, 0.85);
          backdrop-filter: blur(12px);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
          animation: fadeIn 0.3s ease;
        }
        .scanner-container {
          background: var(--bg-1);
          border: 1px solid var(--border);
          border-radius: var(--r-lg);
          width: 100%;
          max-width: 500px;
          overflow: hidden;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
          display: flex;
          flex-direction: column;
        }
        .scanner-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid var(--border);
        }
        .scanner-viewfinder {
          position: relative;
          width: 100%;
          aspect-ratio: 4/3;
          background: #000;
          overflow: hidden;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .scanner-video {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .scanner-target-box {
          position: absolute;
          top: 15%; left: 10%; right: 10%; bottom: 15%;
          border: 2px dashed var(--accent);
          box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
          border-radius: 8px;
          pointer-events: none;
        }
        .scanner-target-box::after {
          content: '';
          position: absolute;
          left: 0; right: 0;
          height: 3px;
          background: linear-gradient(to right, transparent, var(--accent), transparent);
          box-shadow: 0 0 10px var(--accent);
          animation: laserScan 2s linear infinite;
        }
        @keyframes laserScan {
          0% { top: 0%; }
          50% { top: 100%; }
          100% { top: 0%; }
        }
        .ocr-progress-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(10, 15, 30, 0.9);
          color: #fff;
          z-index: 10;
          padding: 20px;
          text-align: center;
        }
        .ocr-spinner {
          width: 48px;
          height: 48px;
          border: 4px solid rgba(255, 255, 255, 0.1);
          border-left-color: var(--accent);
          border-radius: 50%;
          animation: ocrSpin 1s linear infinite;
          margin-bottom: 16px;
        }
        @keyframes ocrSpin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .scanner-footer {
          padding: 16px 20px;
          background: var(--bg-2);
          border-top: 1px solid var(--border);
          display: flex;
          gap: 12px;
        }
        .scanner-error-view {
          padding: 20px;
          text-align: center;
          color: var(--text-2);
          font-size: 0.9rem;
        }
      `}</style>

      <div className="page-head">
        <h1>Fraud Scanner</h1>
        <p>Analyze SMS messages, emails, and URLs for fraud and phishing</p>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, alignItems:'start' }}>
        {/* Input Panel */}
        <div>
          <div style={{ display:'flex', alignItems:'center', gap:12, marginBottom:14 }}>
            <div className="tabs">
              {TYPES.map(t => (
                <button key={t} className={`tab${type===t?' active':''}`} onClick={() => { setType(t); setResult(null); setContent(''); }}>
                  {t.toUpperCase()}
                </button>
              ))}
            </div>
            <div style={{ fontSize:'.78rem', color:'var(--text-3)', display:'flex', alignItems:'center', gap:5 }}>
              <Terminal size={13}/> AI-powered analysis
            </div>
          </div>

          <form onSubmit={handle}>
            <div className="terminal" style={{ marginBottom:12 }}>
              <div className="terminal-bar">
                <div className="terminal-dot r"></div>
                <div className="terminal-dot y"></div>
                <div className="terminal-dot g"></div>
                <span className="terminal-label">veridian:scanner ~ {type}</span>
              </div>
              {type === 'url' ? (
                <input
                  className="terminal-input"
                  style={{ display:'block', minHeight:'auto', padding:'14px 16px', fontFamily:'monospace' }}
                  placeholder={`> Enter URL to analyze…`}
                  value={content}
                  onChange={e => setContent(e.target.value)}
                  required
                />
              ) : (
                <textarea
                  className="terminal-input"
                  placeholder={placeholders[type]}
                  value={content}
                  onChange={e => setContent(e.target.value)}
                  required
                />
              )}
            </div>

            {/* Premium Camera Scan triggers */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ flex: 1, gap: 8, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '8px 12px', fontSize: '.82rem' }}
                onClick={startCamera}
              >
                <Camera size={14} /> Camera Scan
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ flex: 1, gap: 8, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '8px 12px', fontSize: '.82rem' }}
                onClick={triggerFileBrowser}
              >
                <Upload size={14} /> Upload Screenshot
              </button>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept="image/*"
                onChange={handleFileChange}
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>

            {error && <div className="alert alert-error" style={{ marginBottom: 12 }}>{error}</div>}

            <button type="submit" className="btn btn-primary" style={{ width:'100%', gap:8 }} disabled={loading || !content.trim()}>
              <Zap size={16}/> {loading ? 'Analyzing…' : 'Analyze Now'}
            </button>
          </form>

          <div style={{ marginTop:14, padding:12, background:'var(--bg-1)', borderRadius:'var(--r)', border:'1px solid var(--border)', fontSize:'.78rem', color:'var(--text-3)', lineHeight:1.6 }}>
            Uses TF-IDF vectorization + Random Forest + Logistic Regression ensemble with rule-based pattern matching. Results explain which factors triggered the score.
          </div>
        </div>

        {/* Result Panel */}
        <div>
          {loading && (
            <div style={{ background:'var(--bg-1)', border:'1px solid var(--border)', borderRadius:'var(--r-lg)', padding:40, textAlign:'center' }}>
              <div className="spin" style={{ margin:'0 auto 16px' }}></div>
              <div style={{ fontWeight:600 }}>Running AI Analysis</div>
              <div style={{ fontSize:'.8rem', color:'var(--text-3)', marginTop:4 }}>Processing with ML models…</div>
            </div>
          )}

          {result && !loading && (
            <div className="result-card animate" style={{ border:`1px solid ${result.is_fraud ? 'rgba(239,68,68,.2)' : 'rgba(34,197,94,.15)'}` }}>
              <div className="result-header" style={{ background: result.is_fraud ? 'rgba(239,68,68,.04)' : 'rgba(34,197,94,.04)', borderBottom:'1px solid var(--border)' }}>
                <div className="result-icon" style={{ background: result.is_fraud ? 'var(--red-bg)' : 'var(--green-bg)' }}>
                  {result.is_fraud ? <ShieldAlert size={26} color="var(--red)"/> : <ShieldCheck size={26} color="var(--green)"/>}
                </div>
                <div className="result-meta">
                  <h2>{result.is_fraud ? 'Fraud Detected' : 'Appears Safe'}</h2>
                  <div style={{ display:'flex', gap:8, marginTop:6, alignItems:'center' }}>
                    <span className={`badge ${riskBadge(result.risk_category)}`}>{result.risk_category} risk</span>
                    <span style={{ fontSize:'.8rem', color:'var(--text-2)' }}>{result.fraud_probability.toFixed(1)}% confidence</span>
                    <span style={{ fontSize:'.75rem', color:'var(--text-3)' }}>{result.processing_time_ms}ms</span>
                  </div>
                </div>
              </div>

              <div className="result-body">
                <div style={{ margin:'16px 0' }}>
                  <div style={{ display:'flex', justifyContent:'space-between', fontSize:'.78rem', color:'var(--text-3)', marginBottom:6 }}>
                    <span>Risk Score</span><span style={{ color: riskColor(result.risk_category), fontWeight:600 }}>{result.risk_score.toFixed(0)}/100</span>
                  </div>
                  <div className="risk-bar" style={{ height:6 }}>
                    <div className={`risk-bar-fill ${result.risk_category}`} style={{ width:`${result.risk_score}%` }}></div>
                  </div>
                </div>

                <div className="explain-block" style={{ marginBottom:16 }}>
                  <div style={{ fontSize:'.72rem', fontWeight:600, textTransform:'uppercase', letterSpacing:'.5px', color:'var(--text-3)', marginBottom:8 }}>AI Analysis</div>
                  {result.detailed_explanation?.summary || result.explanation}
                </div>

                {result.suspicious_keywords.length > 0 && (
                  <div style={{ marginBottom:16 }}>
                    <div style={{ fontSize:'.72rem', fontWeight:600, textTransform:'uppercase', letterSpacing:'.5px', color:'var(--text-3)', marginBottom:8 }}>Suspicious Signals</div>
                    <div style={{ display:'flex', flexWrap:'wrap', gap:5 }}>
                      {result.suspicious_keywords.slice(0,8).map((kw,i) => (
                        <span key={i} className="badge badge-red">{kw}</span>
                      ))}
                    </div>
                  </div>
                )}

                {Object.keys(result.feature_importance).length > 0 && (
                  <div style={{ marginBottom:16 }}>
                    <div style={{ fontSize:'.72rem', fontWeight:600, textTransform:'uppercase', letterSpacing:'.5px', color:'var(--text-3)', marginBottom:10 }}>Risk Factors</div>
                    {Object.entries(result.feature_importance).slice(0,5).map(([k,v]) => (
                      <div key={k} className="feature-row">
                        <div className="feature-row-head">
                          <span style={{ color:'var(--text-2)', fontSize:'.8rem' }}>{k.replace(/_/g,' ')}</span>
                          <span style={{ fontSize:'.8rem', fontWeight:600 }}>{Number(v).toFixed(1)}%</span>
                        </div>
                        <div className="feature-bar2">
                          <div className="feature-bar2-fill" style={{ width:`${Number(v)}%` }}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {result.detailed_explanation?.recommendations && result.detailed_explanation.recommendations.length > 0 && (
                  <div style={{ padding:'12px 14px', background: result.is_fraud ? 'var(--red-bg)' : 'var(--green-bg)', borderRadius:'var(--r-sm)', border:`1px solid ${result.is_fraud ? 'rgba(239,68,68,.15)' : 'rgba(34,197,94,.15)'}` }}>
                    <div style={{ display:'flex', alignItems:'center', gap:6, fontWeight:600, fontSize:'.82rem', color: result.is_fraud ? 'var(--red)' : 'var(--green)', marginBottom:8 }}>
                      <AlertTriangle size={14}/> Recommended Actions
                    </div>
                    <ul style={{ paddingLeft:16, color:'var(--text-2)', fontSize:'.82rem', display:'flex', flexDirection:'column', gap:4 }}>
                      {result.detailed_explanation.recommendations.slice(0,4).map((r,i) => <li key={i}>{r}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {!result && !loading && (
            <div style={{ background:'var(--bg-1)', border:'1px solid var(--border)', borderRadius:'var(--r-lg)', padding:40, textAlign:'center', color:'var(--text-3)' }}>
              <Terminal size={36} style={{ opacity:.2, marginBottom:12 }}/>
              <div style={{ fontSize:'.875rem' }}>Results will appear here after analysis</div>
            </div>
          )}
        </div>
      </div>

      {/* Floating Futuristic Glassmorphic Camera Scanner Overlay */}
      {cameraActive && (
        <div className="scanner-overlay">
          <div className="scanner-container">
            <div className="scanner-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600 }}>
                <Camera size={18} color="var(--accent)" />
                <span>Camera Scanner</span>
              </div>
              <button onClick={closeScanner} className="btn-close" style={{ background: 'none', border: 'none', color: 'var(--text-2)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {ocrLoading && (
              <div className="ocr-progress-container">
                <div className="ocr-spinner"></div>
                <h3 style={{ margin: '0 0 8px', fontWeight: 600 }}>Processing Image</h3>
                <p style={{ fontSize: '.85rem', color: 'var(--text-3)' }}>{ocrProgress}</p>
              </div>
            )}

            {cameraError ? (
              <div className="scanner-error-view">
                <p style={{ marginBottom: 16 }}>{cameraError}</p>
                <button className="btn btn-primary" onClick={triggerFileBrowser}>
                  <Upload size={16} style={{ marginRight: 6 }} /> Choose Screenshot File
                </button>
              </div>
            ) : (
              <div className="scanner-viewfinder">
                <video ref={videoRef} className="scanner-video" playsInline muted />
                <div className="scanner-target-box"></div>
              </div>
            )}

            <div className="scanner-footer">
              <button onClick={closeScanner} className="btn btn-secondary" style={{ flex: 1 }}>
                Cancel
              </button>
              {!cameraError && (
                <button onClick={capturePhoto} className="btn btn-primary" style={{ flex: 2, gap: 8 }}>
                  <Eye size={16} /> Capture & Read
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanPage;
