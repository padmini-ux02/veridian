export interface User {
  id: string; email: string; username: string; full_name: string;
  role: 'admin' | 'user'; is_active: boolean; avatar_url?: string;
  phone?: string; created_at: string; last_login?: string;
}
export interface AuthResponse { access_token: string; token_type: string; user: User; }
export interface ScanRequest { scan_type: 'sms' | 'email' | 'url'; content: string; }
export interface ScanResult {
  id: string; scan_type: string; input_content: string; is_fraud: boolean;
  fraud_probability: number; risk_category: string; risk_score: number;
  explanation: string; suspicious_keywords: string[]; feature_importance: Record<string, number>;
  model_used: string; processing_time_ms: number; created_at: string;
  detailed_explanation?: ExplanationDetail;
}
export interface ExplanationDetail {
  summary: string; risk_category: string; fraud_probability: number;
  risk_factors: RiskFactor[]; highlighted_content: string;
  suspicious_keywords: string[]; recommendations: string[];
  educational_tips: string[]; scan_type: string;
}
export interface RiskFactor {
  name: string; description: string; icon: string;
  importance: number; severity: string;
}
export interface ScanHistory { scans: ScanResult[]; total: number; page: number; page_size: number; total_pages: number; }
export interface ScanStats {
  total_scans: number; fraud_detected: number; safe_detected: number;
  high_risk_count: number; medium_risk_count: number; low_risk_count: number;
  sms_scans: number; email_scans: number; url_scans: number;
  average_risk_score: number; scans_by_date: { date: string; total: number; fraud: number }[];
}
export interface Report {
  id: string; user_id: string; report_type: string; title: string; content: string;
  description?: string; source?: string; status: string; admin_notes?: string;
  reviewed_by?: string; reviewed_at?: string; created_at: string; updated_at: string;
  reporter_username?: string;
}
export interface Alert {
  id: string; user_id: string; alert_type: string; title: string;
  message: string; scan_id?: string; is_read: boolean; created_at: string;
}
export interface ChatMessage { role: 'user' | 'assistant'; content: string; intent?: string; }
export interface AdminStats extends ScanStats {
  total_users: number; fraud_trends: { date: string; total: number; fraud: number; safe: number }[];
  recent_scans: { id: string; scan_type: string; risk_category: string; fraud_probability: number; created_at: string }[];
  reports: { total_reports: number; pending: number; reviewing: number; confirmed_fraud: number; dismissed: number };
}
