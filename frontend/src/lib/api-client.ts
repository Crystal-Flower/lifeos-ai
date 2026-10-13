const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || 'API Request failed');
    }
    
    return res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Auth
  getMe: () => request<any>('/auth/me'),
  getSettings: () => request<any>('/auth/settings'),
  updateSettings: (data: any) => request<any>('/auth/settings', { method: 'PUT', body: JSON.stringify(data) }),
  
  // Tasks
  getTasks: (filters?: { status?: string; priority?: string }) => {
    const params = new URLSearchParams(filters as any).toString();
    return request<any[]>(`/tasks/${params ? `?${params}` : ''}`);
  },
  createTask: (data: any) => request<any>('/tasks/', { method: 'POST', body: JSON.stringify(data) }),
  quickParseTask: (text: string) => request<any>('/tasks/quick-parse', { method: 'POST', body: JSON.stringify({ text }) }),
  testReminder: () => request<any>('/tasks/test-reminder', { method: 'POST' }),
  updateTask: (id: string, data: any) => request<any>(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTask: (id: string) => request<any>(`/tasks/${id}`, { method: 'DELETE' }),

  // Habits
  getHabits: () => request<any[]>('/habits/'),
  createHabit: (data: any) => request<any>('/habits/', { method: 'POST', body: JSON.stringify(data) }),
  logHabit: (id: string) => request<any>(`/habits/${id}/log`, { method: 'POST' }),
  deleteHabit: (id: string) => request<any>(`/habits/${id}`, { method: 'DELETE' }),

  // Projects
  getProjects: () => request<any[]>('/projects/'),
  createProject: (data: any) => request<any>('/projects/', { method: 'POST', body: JSON.stringify(data) }),
  updateProject: (id: string, data: any) => request<any>(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProject: (id: string) => request<any>(`/projects/${id}`, { method: 'DELETE' }),
  getMilestones: (projectId: string) => request<any[]>(`/projects/${projectId}/milestones`),
  createMilestone: (projectId: string, data: any) => request<any>(`/projects/${projectId}/milestones`, { method: 'POST', body: JSON.stringify(data) }),
  updateMilestone: (milestoneId: string, data: any) => request<any>(`/projects/milestones/${milestoneId}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Competitions
  getCompetitions: () => request<any[]>('/competitions/'),
  createCompetition: (data: any) => request<any>('/competitions/', { method: 'POST', body: JSON.stringify(data) }),
  updateCompetition: (id: string, data: any) => request<any>(`/competitions/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteCompetition: (id: string) => request<any>(`/competitions/${id}`, { method: 'DELETE' }),
  getMembers: (compId: string) => request<any[]>(`/competitions/${compId}/members`),
  addMember: (compId: string, data: any) => request<any>(`/competitions/${compId}/members`, { method: 'POST', body: JSON.stringify(data) }),
  removeMember: (memberId: string) => request<any>(`/competitions/members/${memberId}`, { method: 'DELETE' }),

  // Notes
  getNotes: () => request<any[]>('/notes/'),
  createNote: (data: any) => request<any>('/notes/', { method: 'POST', body: JSON.stringify(data) }),
  updateNote: (id: string, data: any) => request<any>(`/notes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteNote: (id: string) => request<any>(`/notes/${id}`, { method: 'DELETE' }),
  summarizeNote: (id: string) => request<any>(`/notes/${id}/summarize`, { method: 'POST' }),

  // Calendar
  getCalendarEvents: () => request<any[]>('/calendar/'),
  syncCalendar: () => request<any>('/calendar/sync', { method: 'POST' }),
  getCalendarAuthUrl: () => request<{ url: string; simulated: boolean }>('/calendar/auth-url'),

  // AI Scheduler
  autoSchedule: () => request<any>('/scheduler/auto-schedule', { method: 'POST' }),

  // Reminders
  snoozeReminder: (id: string, minutes: number) => request<any>(`/reminders/${id}/snooze`, { method: 'POST', body: JSON.stringify({ minutes }) }),

  // Analytics
  getAnalytics: () => request<any>('/analytics/'),

  // AI Chief of Staff
  chat: (message: string) => request<{ reply: string }>('/ai/chat', { method: 'POST', body: JSON.stringify({ message }) }),
  getDailyBriefing: () => request<{ briefing: string }>('/ai/daily-briefing'),
};
