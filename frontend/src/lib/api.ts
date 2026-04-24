import axios from 'axios'

const api = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  const customBase = localStorage.getItem('api_base_url')
  if (customBase) {
    config.baseURL = customBase
  }
  return config
})

export interface Issue {
  rule: string
  severity: string
  line: number
  message: string
  suggestion: string
}

export interface SecurityFlag {
  rule: string
  severity: string
  line: number
  message: string
  recommendation: string
}

export interface ScoreBreakdown {
  overall: number
  clean_code: number
  readability: number
  maintainability: number
  security: number
  ml_quality: number
  explanations: Record<string, string[]>
}

export interface MLPrediction {
  quality_label: string
  confidence: number
  probabilities: Record<string, number>
  meets_threshold: boolean
}

export interface ComplexityMetrics {
  cyclomatic_complexity: number
  maintainability_index: number
  lines_of_code: number
  source_lines_of_code: number
  comment_ratio: number
  function_count: number
  class_count: number
}

export interface ReviewResult {
  id: string
  issues: Issue[]
  suggestions: string[]
  score: number
  score_breakdown: ScoreBreakdown
  security_flags: SecurityFlag[]
  ml_prediction: MLPrediction | null
  complexity_metrics: ComplexityMetrics
  summary: string
  version: number
  reviewed_at: string
  cached: boolean
}

export interface ReviewListItem {
  id: string
  language: string
  score: number
  issue_count: number
  security_flag_count: number
  ml_quality_label: string | null
  reviewed_at: string
  code: string
}

export interface ReviewListResponse {
  total: number
  reviews: ReviewListItem[]
}

export interface BatchReviewResponse {
  reviews: ReviewResult[]
  summary: {
    total_files: number
    average_score: number
    min_score: number
    max_score: number
    total_issues: number
    total_security_flags: number
  }
}

export interface VersionHistory {
  code_hash: string
  total_versions: number
  versions: Array<{
    id: string
    score: number
    clean_code_score: number
    readability_score: number
    maintainability_score: number
    security_score: number
    ml_quality_score: number
    issue_count: number
    security_flag_count: number
    version: number
    reviewed_at: string
  }>
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user_id: string
  username: string
}

export interface UserInfo {
  id: string
  email: string
  username: string
  review_count: number
}

export const reviewApi = {
  submit: (code: string, language: string) =>
    api.post<ReviewResult>('/api/v1/review', { code, language }),

  submitBatch: (items: Array<{ code: string; language: string; filename?: string }>) =>
    api.post<BatchReviewResponse>('/api/v1/review-batch', { items }),

  getById: (id: string) =>
    api.get<ReviewResult>(`/api/v1/review/${id}`),

  list: (skip = 0, limit = 20) =>
    api.get<ReviewListResponse>('/api/v1/reviews', { params: { skip, limit } }),

  getHistory: (id: string) =>
    api.get<VersionHistory>(`/api/v1/reviews/${id}/history`),
}

export const authApi = {
  register: (email: string, username: string, password: string) =>
    api.post<AuthResponse>('/api/v1/auth/register', { email, username, password }),

  login: (email: string, password: string) =>
    api.post<AuthResponse>('/api/v1/auth/login', { email, password }),

  me: () =>
    api.get<UserInfo>('/api/v1/auth/me'),
}

export const healthApi = {
  check: () => api.get<{ status: string; version: string }>('/health'),
}

export default api
