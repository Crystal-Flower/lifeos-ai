'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  LayoutDashboard, CheckSquare, Calendar, Trophy, FolderKanban, 
  BookOpen, Award, Settings as SettingsIcon, Plus, Trash2, Check, 
  AlertCircle, RefreshCw, Brain, Bot, Send, User, ChevronRight, CheckCircle2,
  CalendarCheck, Clock, Flame, Percent, Activity, Bell, X, Sparkles, Link as LinkIcon
} from 'lucide-react';
import { api } from '@/lib/api-client';

// Type Definitions
interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'TODO' | 'IN_PROGRESS' | 'DONE' | 'ARCHIVED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  dueDate?: string;
  estimatedMinutes?: number;
  scheduledStart?: string;
  scheduledEnd?: string;
  projectId?: string;
}

interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  startTime: string;
  endTime: string;
}

interface Habit {
  id: string;
  name: string;
  streak: number;
  frequency: string;
}

interface Goal {
  id: string;
  title: string;
  progress: number;
  targetDate?: string;
}

interface Project {
  id: string;
  name: string;
  description?: string;
  progress: number;
  status: string;
  githubRepo?: string;
  dependencies?: Record<string, string[]>;
  predictionData?: Record<string, any>;
}

interface Competition {
  id: string;
  title: string;
  description?: string;
  progress: number;
  reportSubmitted: boolean;
  pptSubmitted: boolean;
  demoLink?: string;
  githubUrl?: string;
  timelineData?: any[];
  documents?: any[];
  checklist?: any[];
}

interface Note {
  id: string;
  title: string;
  content: string;
  summary?: string;
  tags: string[];
}

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  urgency: string;
  time: string;
}

interface Analytics {
  completionRate: number;
  focusTimeMinutes: number;
  missedDeadlinesCount: number;
  burnoutRisk: 'LOW' | 'MEDIUM' | 'HIGH';
  habitScore: number;
  chartData: { date: string; completed: number; total: number }[];
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'tasks' | 'competitions' | 'projects' | 'notes' | 'habits' | 'settings'>('dashboard');
  
  // Data States
  const [tasks, setTasks] = useState<Task[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  
  // Real-time notification states
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [activeAlert, setActiveAlert] = useState<NotificationItem | null>(null);
  
  // UI & Form States
  const [newTaskText, setNewTaskText] = useState('');
  const [parsingTask, setParsingTask] = useState(false);
  const [syncingCalendar, setSyncingCalendar] = useState(false);
  const [testingReminder, setTestingReminder] = useState(false);
  const [aiBriefing, setAiBriefing] = useState<string>('Booting up LifeOS AI Chief of Staff...');
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<{role: 'user' | 'assistant', text: string}[]>([
    { role: 'assistant', text: 'Hello Anandhappriya! I am your AI Chief of Staff. How can I assist you with your day?' }
  ]);
  const [sendingChat, setSendingChat] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // New Entity Inputs
  const [habitInput, setHabitInput] = useState('');
  const [goalInput, setGoalInput] = useState('');
  const [noteTitleInput, setNoteTitleInput] = useState('');
  const [noteContentInput, setNoteContentInput] = useState('');
  const [projectInput, setProjectInput] = useState('');
  const [compInput, setCompInput] = useState('');

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Load Data on Mount
  useEffect(() => {
    fetchData();
  }, []);

  // WebSocket connection for real-time notifications
  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWS = () => {
      const wsUrl = 'ws://127.0.0.1:8000/api/v1/ws/default-user-id';
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log("Real-time WebSocket tunnel connected.");
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("WebSocket event received:", data);
          
          if (data.type === 'REMINDER') {
            const newNotification: NotificationItem = {
              id: data.id || Math.random().toString(),
              title: data.title || "Reminder Due",
              message: data.message || "",
              urgency: data.urgency || "URGENT",
              time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

            setActiveAlert(newNotification);
            setNotifications(prev => [newNotification, ...prev]);
            fetchData();
          }
        } catch (err) {
          console.error("Failed to parse real-time event", err);
        }
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed. Reconnecting in 3s...");
        reconnectTimeout = setTimeout(connectWS, 3000);
      };

      socket.onerror = (err) => {
        console.error("WebSocket connection error:", err);
      };
    };

    connectWS();

    return () => {
      if (socket) socket.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const me = await api.getMe().catch(() => ({ email: 'anandhappriya@gmail.com' }));
      
      const loadedTasks = await api.getTasks().catch(() => mockData.tasks);
      const loadedEvents = await api.getCalendarEvents().catch(() => mockData.events);
      const loadedHabits = await api.getHabits().catch(() => mockData.habits);
      const loadedNotes = await api.getNotes().catch(() => mockData.notes);
      const loadedProjects = await api.getProjects().catch(() => mockData.projects);
      const loadedComps = await api.getCompetitions().catch(() => mockData.competitions);
      const loadedAnalytics = await api.getAnalytics().catch(() => mockData.analytics);
      
      const loadedGoals = mockData.goals; 

      setTasks(loadedTasks);
      setEvents(loadedEvents);
      setHabits(loadedHabits);
      setGoals(loadedGoals);
      setNotes(loadedNotes);
      setProjects(loadedProjects);
      setCompetitions(loadedComps);
      setAnalytics(loadedAnalytics);

      const brief = await api.getDailyBriefing().catch(() => ({ briefing: defaultBriefingText }));
      setAiBriefing(brief.briefing);

    } catch (err) {
      console.error("Error loading system dashboard", err);
    } finally {
      setLoading(false);
    }
  };

  // Google Calendar Auth URL Redirect
  const handleConnectGoogleCalendar = async () => {
    try {
      const res = await api.getCalendarAuthUrl();
      window.location.href = res.url;
    } catch (err) {
      console.error("Failed to generate authorization URL", err);
    }
  };

  // AI Auto-Scheduler Trigger
  const handleAutoSchedule = async () => {
    setLoading(true);
    try {
      const res = await api.autoSchedule();
      setNotifications(prev => [
        {
          id: Math.random().toString(),
          title: "AI Auto-Scheduler Run",
          message: `Scheduled ${res.scheduledCount} task(s). ${res.warnings.join(' ')}`,
          urgency: "LOW",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
        ...prev
      ]);
      await fetchData();
    } catch (err) {
      console.error("AI Auto-Scheduler trigger failed", err);
    } finally {
      setLoading(false);
    }
  };

  // Smart Snooze trigger
  const handleSnooze = async (id: string, mins: number) => {
    try {
      await api.snoozeReminder(id, mins);
      setNotifications(prev => [
        {
          id: Math.random().toString(),
          title: "Reminder Snoozed",
          message: `Alert snoozed for ${mins} minutes.`,
          urgency: "LOW",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
        ...prev
      ]);
      setActiveAlert(null);
      fetchData();
    } catch (err) {
      console.error("Snooze API call failed", err);
      setActiveAlert(null);
    }
  };

  // Quick Task Parser
  const handleQuickTaskParse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskText.trim()) return;
    setParsingTask(true);
    try {
      const created = await api.quickParseTask(newTaskText);
      setTasks(prev => [created, ...prev]);
      setNewTaskText('');
      api.getDailyBriefing().then(b => setAiBriefing(b.briefing));
      api.getAnalytics().then(a => setAnalytics(a));
    } catch (err) {
      const fallbackTask: Task = {
        id: Math.random().toString(),
        title: newTaskText,
        status: 'TODO',
        priority: newTaskText.toLowerCase().includes('urgent') ? 'URGENT' : 'MEDIUM'
      };
      setTasks(prev => [fallbackTask, ...prev]);
      setNewTaskText('');
    } finally {
      setParsingTask(false);
    }
  };

  // Trigger Real-Time Test Reminder
  const handleTriggerTestReminder = async () => {
    setTestingReminder(true);
    try {
      await api.testReminder();
      setNotifications(prev => [
        {
          id: Math.random().toString(),
          title: "Scheduler Triggered",
          message: "Real-time task reminder will fire in 5 seconds. Watch the screen...",
          urgency: "LOW",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
        ...prev
      ]);
    } catch (err) {
      console.error("Test reminder schedule failed");
    } finally {
      setTestingReminder(false);
    }
  };

  // Toggle Task Status
  const toggleTaskStatus = async (task: Task) => {
    const nextStatusMap: Record<string, 'TODO' | 'IN_PROGRESS' | 'DONE'> = {
      'TODO': 'IN_PROGRESS',
      'IN_PROGRESS': 'DONE',
      'DONE': 'TODO'
    };
    const nextStatus = nextStatusMap[task.status] || 'TODO';
    
    setTasks(prev => prev.map(t => t.id === task.id ? { ...t, status: nextStatus } : t));
    
    try {
      await api.updateTask(task.id, { status: nextStatus });
      api.getAnalytics().then(a => setAnalytics(a));
    } catch (err) {
      console.warn("Offline local task state preserved");
    }
  };

  // Sync Calendar
  const handleSyncCalendar = async () => {
    setSyncingCalendar(true);
    try {
      const res = await api.syncCalendar();
      const updatedEvents = await api.getCalendarEvents();
      setEvents(updatedEvents);
      const brief = await api.getDailyBriefing();
      setAiBriefing(brief.briefing);
    } catch (err) {
      console.error("Calendar Sync failed");
    } finally {
      setSyncingCalendar(false);
    }
  };

  // Send AI message
  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;
    
    const userMsg = chatMessage;
    setChatMessage('');
    setChatHistory(prev => [...prev, { role: 'user', text: userMsg }]);
    setSendingChat(true);

    try {
      const res = await api.chat(userMsg);
      setChatHistory(prev => [...prev, { role: 'assistant', text: res.reply }]);
      fetchData(); // Reload workspace data since AI command might have run scheduler
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', text: "I'm offline, but I'm checking your schedules locally. Keep focusing on your high-priority items!" }]);
    } finally {
      setSendingChat(false);
    }
  };

  const handleDeleteTask = async (id: string) => {
    setTasks(prev => prev.filter(t => t.id !== id));
    api.deleteTask(id).catch(() => {});
  };

  const logHabitStreak = async (id: string) => {
    setHabits(prev => prev.map(h => h.id === id ? { ...h, streak: h.streak + 1 } : h));
    api.logHabit(id).catch(() => {});
  };

  const handleSummarizeNote = async (id: string) => {
    try {
      const updated = await api.summarizeNote(id);
      setNotes(prev => prev.map(n => n.id === id ? updated : n));
    } catch (err) {
      setNotes(prev => prev.map(n => n.id === id ? { ...n, summary: "Focus is vital. Setup workspace early." } : n));
    }
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteTitleInput.trim() || !noteContentInput.trim()) return;
    try {
      const created = await api.createNote({ title: noteTitleInput, content: noteContentInput });
      setNotes(prev => [created, ...prev]);
      setNoteTitleInput('');
      setNoteContentInput('');
    } catch (err) {
      const fallback: Note = {
        id: Math.random().toString(),
        title: noteTitleInput,
        content: noteContentInput,
        tags: []
      };
      setNotes(prev => [fallback, ...prev]);
      setNoteTitleInput('');
      setNoteContentInput('');
    }
  };

  const handleCreateHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!habitInput.trim()) return;
    try {
      const created = await api.createHabit({ name: habitInput, frequency: 'DAILY' });
      setHabits(prev => [...prev, created]);
      setHabitInput('');
    } catch (err) {
      const fallback: Habit = { id: Math.random().toString(), name: habitInput, streak: 0, frequency: 'DAILY' };
      setHabits(prev => [...prev, fallback]);
      setHabitInput('');
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectInput.trim()) return;
    try {
      const created = await api.createProject({ name: projectInput, progress: 0.0, status: 'ACTIVE' });
      setProjects(prev => [...prev, created]);
      setProjectInput('');
    } catch (err) {
      const fallback: Project = { id: Math.random().toString(), name: projectInput, progress: 0, status: 'ACTIVE' };
      setProjects(prev => [...prev, fallback]);
      setProjectInput('');
    }
  };

  const handleCreateComp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!compInput.trim()) return;
    try {
      const created = await api.createCompetition({ title: compInput, progress: 0.0 });
      setCompetitions(prev => [...prev, created]);
      setCompInput('');
    } catch (err) {
      const fallback: Competition = { id: Math.random().toString(), title: compInput, progress: 0, reportSubmitted: false, pptSubmitted: false };
      setCompetitions(prev => [...prev, fallback]);
      setCompInput('');
    }
  };

  const handleToggleCompChecklist = async (comp: Competition, field: 'pptSubmitted' | 'reportSubmitted') => {
    const updatedVal = !comp[field];
    const updatePayload = { [field]: updatedVal };
    
    setCompetitions(prev => prev.map(c => {
      if (c.id === comp.id) {
        const nextComp = { ...c, ...updatePayload };
        let prog = 0.0;
        if (nextComp.pptSubmitted) prog += 25.0;
        if (nextComp.reportSubmitted) prog += 25.0;
        if (nextComp.demoLink) prog += 25.0;
        if (nextComp.githubUrl) prog += 25.0;
        nextComp.progress = prog;
        return nextComp;
      }
      return c;
    }));

    try {
      await api.updateCompetition(comp.id, updatePayload);
    } catch (err) {
      console.warn("Offline competition checklist state preserved");
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#09090b] text-[#fafafa] relative">
      
      {/* REAL-TIME REMINDER POPUP (WITH SMART SNOOZE) */}
      {activeAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-96 glass-panel border border-red-500/20 bg-zinc-950 p-6 rounded-2xl shadow-2xl relative space-y-4">
            <button 
              onClick={() => setActiveAlert(null)}
              className="absolute top-4 right-4 text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
                <AlertCircle className="w-5 h-5 animate-bounce" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-red-400">{activeAlert.title}</h4>
                <p className="text-[10px] text-zinc-500 font-semibold font-mono">Real-Time Reminder Engine</p>
              </div>
            </div>
            <p className="text-xs text-zinc-200 leading-relaxed font-medium bg-zinc-900 p-3 rounded-lg border border-zinc-850">
              {activeAlert.message}
            </p>
            <div className="flex gap-2 justify-end pt-1">
              <button 
                onClick={() => handleSnooze(activeAlert.id, 5)}
                className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 hover:bg-zinc-805 rounded-lg text-xs text-zinc-400 font-medium transition-all"
              >
                Snooze 5m
              </button>
              <button 
                onClick={() => setActiveAlert(null)}
                className="px-3 py-1.5 bg-white hover:bg-zinc-200 rounded-lg text-xs text-black font-bold transition-all"
              >
                Acknowledge
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 1. Sidebar Navigation */}
      <aside className="w-64 border-r border-[#27272a]/70 bg-[#09090b] flex flex-col justify-between p-6">
        <div>
          <div className="flex items-center gap-3 mb-8">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-white text-black font-bold text-xl shadow-lg">
              Ω
            </div>
            <div>
              <h1 className="font-bold tracking-tight text-md">LifeOS AI</h1>
              <span className="text-xs text-zinc-500 font-medium">Personal Operating System</span>
            </div>
          </div>

          <nav className="space-y-1.5">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { id: 'tasks', label: 'AI Task Manager', icon: CheckSquare },
              { id: 'competitions', label: 'Competitions Hub', icon: Trophy },
              { id: 'projects', label: 'Projects Kanban', icon: FolderKanban },
              { id: 'notes', label: 'Second Brain Notes', icon: BookOpen },
              { id: 'habits', label: 'Habits & Goals', icon: Award },
              { id: 'settings', label: 'System Settings', icon: SettingsIcon },
            ].map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id as any)}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive 
                      ? 'bg-zinc-800 text-white shadow-sm' 
                      : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-zinc-500'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* User Mini Card */}
        <div className="pt-6 border-t border-[#27272a]/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-300 font-bold border border-zinc-700">
              A
            </div>
            <div>
              <p className="text-xs font-semibold text-zinc-200">Anandhappriya S</p>
              <p className="text-[10px] text-zinc-500">anandhappriya@gmail.com</p>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. Main Content Container */}
      <main className="flex-1 flex flex-col overflow-y-auto bg-[#09090b] relative">
        {/* Header Bar */}
        <header className="sticky top-0 z-10 glass-panel border-b border-[#27272a]/40 px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold capitalize tracking-tight">{activeTab}</h2>
            <button 
              onClick={handleAutoSchedule}
              className="flex items-center gap-1.5 px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-indigo-400 border border-zinc-700 rounded-lg text-xs font-bold transition-all cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              AI Auto-Schedule
            </button>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={handleTriggerTestReminder}
              disabled={testingReminder}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-xs font-semibold text-red-400 transition-all cursor-pointer"
            >
              <Bell className="w-3.5 h-3.5" />
              Test Alert
            </button>
            <button 
              onClick={fetchData}
              className="p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition-all"
              title="Refresh Space"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
            <button 
              onClick={handleSyncCalendar}
              disabled={syncingCalendar}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs font-medium text-zinc-300 transition-all"
            >
              <CalendarCheck className="w-3.5 h-3.5 text-indigo-400" />
              {syncingCalendar ? 'Syncing...' : 'Sync Calendar'}
            </button>
          </div>
        </header>

        {/* Dynamic Panels */}
        <div className="p-8 max-w-7xl w-full mx-auto space-y-8 flex-1">
          {loading ? (
            <div className="h-64 flex flex-col items-center justify-center text-zinc-400 gap-3">
              <RefreshCw className="w-6 h-6 animate-spin text-zinc-500" />
              <p className="text-xs font-semibold">Initializing LifeOS Modules...</p>
            </div>
          ) : (
            <>
              {/* TAB 1: DASHBOARD */}
              {activeTab === 'dashboard' && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  {/* Executive AI briefing panel */}
                  <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 blur-3xl rounded-full pointer-events-none"></div>
                    <div className="absolute bottom-0 left-0 w-48 h-48 bg-emerald-500/5 blur-3xl rounded-full pointer-events-none"></div>
                    
                    <div className="flex items-start gap-4">
                      <div className="p-3 bg-zinc-800/80 rounded-xl border border-zinc-700">
                        <Brain className="w-6 h-6 text-zinc-100" />
                      </div>
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-zinc-400 tracking-wider uppercase">AI Daily Briefing & Insights</h3>
                          <span className="text-[10px] font-bold px-2 py-0.5 bg-zinc-800 text-zinc-300 rounded border border-zinc-700">Today</span>
                        </div>
                        <pre className="text-zinc-200 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                          {aiBriefing}
                        </pre>
                      </div>
                    </div>
                  </div>

                  {/* Core Metrics Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="glass-card rounded-xl p-5 border border-zinc-800/60 flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-xs text-zinc-500 font-semibold">Task Rate</p>
                        <p className="text-2xl font-bold font-mono">
                          {analytics ? `${analytics.completionRate}%` : '50%'}
                        </p>
                      </div>
                      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-880">
                        <Percent className="w-5 h-5 text-indigo-400" />
                      </div>
                    </div>
                    <div className="glass-card rounded-xl p-5 border border-zinc-800/60 flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-xs text-zinc-500 font-semibold">Focus Time</p>
                        <p className="text-2xl font-bold font-mono">
                          {analytics ? `${analytics.focusTimeMinutes}m` : '0m'}
                        </p>
                      </div>
                      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-880">
                        <Clock className="w-5 h-5 text-emerald-400" />
                      </div>
                    </div>
                    <div className="glass-card rounded-xl p-5 border border-zinc-800/60 flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-xs text-zinc-500 font-semibold">Overdue Deadlines</p>
                        <p className="text-2xl font-bold font-mono text-red-400">
                          {analytics ? analytics.missedDeadlinesCount : 0}
                        </p>
                      </div>
                      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-880">
                        <AlertCircle className="w-5 h-5 text-red-400" />
                      </div>
                    </div>
                    <div className="glass-card rounded-xl p-5 border border-zinc-800/60 flex items-center justify-between">
                      <div className="space-y-1">
                        <p className="text-xs text-zinc-500 font-semibold">Cognitive Load</p>
                        <p className={`text-2xl font-bold font-mono ${
                          analytics?.burnoutRisk === 'HIGH' ? 'text-red-400' : 
                          analytics?.burnoutRisk === 'MEDIUM' ? 'text-amber-400' : 'text-zinc-200'
                        }`}>
                          {analytics ? analytics.burnoutRisk : 'LOW'}
                        </p>
                      </div>
                      <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-880">
                        <Activity className="w-5 h-5 text-rose-400" />
                      </div>
                    </div>
                  </div>

                  {/* Grid Section: Schedule vs Quick Capture */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Schedule block */}
                    <div className="glass-card rounded-xl p-6 border border-zinc-800 lg:col-span-2 space-y-4">
                      <div className="flex items-center justify-between border-b border-zinc-800/50 pb-3">
                        <h4 className="font-semibold text-sm flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-indigo-400" /> Upcoming Schedule
                        </h4>
                      </div>
                      <div className="space-y-3">
                        {events.length ? (
                          events.map(event => (
                            <div key={event.id} className="flex gap-4 p-3 rounded-lg bg-zinc-900/40 border border-zinc-850 hover:bg-zinc-900/80 transition-all">
                              <div className="w-16 flex flex-col items-center justify-center bg-zinc-900 border border-zinc-800 rounded px-1 py-1.5 text-center font-mono">
                                <span className="text-[10px] text-zinc-400 font-bold">START</span>
                                <span className="text-xs font-extrabold text-indigo-300">{new Date(event.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                              </div>
                              <div className="flex-1 space-y-0.5">
                                <h5 className="text-sm font-semibold text-zinc-200">{event.title}</h5>
                                <p className="text-xs text-zinc-500 line-clamp-1">{event.description || 'No description provided'}</p>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-6 text-zinc-500 text-xs">No upcoming calendar events. Click Sync above!</div>
                        )}
                      </div>
                    </div>

                    {/* Chart visual block */}
                    <div className="glass-card rounded-xl p-6 border border-zinc-800 space-y-4 flex flex-col justify-between">
                      <h4 className="font-semibold text-sm flex items-center gap-2 border-b border-zinc-800/50 pb-3">
                        <Activity className="w-4 h-4 text-emerald-400" /> Completion Rate Trend
                      </h4>
                      <div className="flex-1 flex items-end justify-between gap-2 h-32 pt-4">
                        {analytics?.chartData.map((d, index) => {
                          const rate = Math.round((d.completed / d.total) * 100) || 0;
                          return (
                            <div key={index} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                              <div className="w-full bg-zinc-900 rounded-md overflow-hidden relative flex flex-col justify-end border border-zinc-800" style={{ height: '80%' }}>
                                <div className="bg-indigo-500 w-full rounded-md transition-all duration-300" style={{ height: `${rate}%` }}></div>
                              </div>
                              <span className="text-[8px] font-bold text-zinc-500 font-mono text-center truncate w-full">{d.date}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: TASKS KANBAN */}
              {activeTab === 'tasks' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">AI Task Boards</h3>
                    
                    <form onSubmit={handleQuickTaskParse} className="flex gap-2 w-1/2">
                      <input 
                        type="text" 
                        value={newTaskText} 
                        onChange={e => setNewTaskText(e.target.value)}
                        placeholder="NLP task creation: Finish homework today at 6pm" 
                        className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none"
                      />
                      <button type="submit" className="px-3 bg-zinc-100 hover:bg-zinc-300 text-black font-bold text-xs rounded-lg flex items-center gap-1.5">
                        <Plus className="w-3.5 h-3.5" /> Parse
                      </button>
                    </form>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {['TODO', 'IN_PROGRESS', 'DONE'].map(col => {
                      const colTasks = tasks.filter(t => t.status === col);
                      const colTitle = col === 'TODO' ? 'To Do' : col === 'IN_PROGRESS' ? 'In Progress' : 'Done';
                      return (
                        <div key={col} className="glass-card rounded-xl p-5 border border-zinc-800 space-y-4">
                          <div className="flex items-center justify-between border-b border-zinc-850 pb-2">
                            <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">{colTitle} ({colTasks.length})</h4>
                          </div>

                          <div className="space-y-3">
                            {colTasks.length ? (
                              colTasks.map(task => (
                                <div key={task.id} className="p-4 rounded-lg bg-zinc-900 border border-zinc-800/80 hover:border-zinc-700 transition-all space-y-3">
                                  <div className="flex items-start justify-between gap-2">
                                    <h5 className="text-xs font-semibold text-zinc-100 line-clamp-2">{task.title}</h5>
                                    <button 
                                      onClick={() => handleDeleteTask(task.id)}
                                      className="text-zinc-600 hover:text-rose-400 p-0.5 rounded transition-colors"
                                    >
                                      <Trash2 className="w-3 h-3" />
                                    </button>
                                  </div>
                                  
                                  {task.description && (
                                    <p className="text-[10px] text-zinc-500 line-clamp-2">{task.description}</p>
                                  )}

                                  {task.scheduledStart && (
                                    <div className="flex items-center gap-1 text-[9px] text-indigo-400 font-bold bg-indigo-500/5 px-2 py-1 rounded border border-indigo-500/10 font-mono">
                                      <Clock className="w-2.5 h-2.5" />
                                      <span>Scheduled: {new Date(task.scheduledStart).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                  )}

                                  <div className="flex items-center justify-between pt-1">
                                    <span className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded ${
                                      task.priority === 'URGENT' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                                      task.priority === 'HIGH' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                                      'bg-zinc-800 text-zinc-400 border border-zinc-700'
                                    }`}>
                                      {task.priority}
                                    </span>

                                    <button 
                                      onClick={() => toggleTaskStatus(task)}
                                      className="px-2 py-0.5 bg-zinc-800 hover:bg-zinc-700 text-[10px] font-medium text-zinc-300 rounded border border-zinc-700 flex items-center gap-1 transition-all"
                                    >
                                      {col === 'DONE' ? 'Redo' : 'Next'} <ChevronRight className="w-2.5 h-2.5" />
                                    </button>
                                  </div>
                                </div>
                              ))
                            ) : (
                              <div className="text-center py-8 text-zinc-600 text-xs font-medium">Empty Column</div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* TAB 3: COMPETITIONS */}
              {activeTab === 'competitions' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                    <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">Competition Timeline</h3>
                    <form onSubmit={handleCreateComp} className="flex gap-2">
                      <input 
                        type="text" 
                        placeholder="Add hackathon target..." 
                        value={compInput}
                        onChange={e => setCompInput(e.target.value)}
                        className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none placeholder-zinc-600"
                      />
                      <button type="submit" className="px-3 bg-zinc-100 hover:bg-zinc-300 text-black text-xs font-semibold rounded-lg">
                        Add
                      </button>
                    </form>
                  </div>

                  <div className="grid grid-cols-1 gap-4">
                    {competitions.length ? (
                      competitions.map(comp => (
                        <div key={comp.id} className="glass-card rounded-xl p-5 border border-zinc-800 space-y-4">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="text-sm font-semibold text-zinc-100">{comp.title}</h4>
                              <p className="text-xs text-zinc-500 mt-0.5">{comp.description || 'Competition portfolio tracking'}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold text-zinc-400">Progress:</span>
                              <span className="text-xs font-extrabold text-indigo-400 font-mono">{comp.progress}%</span>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
                            <label className="flex items-center gap-2.5 p-3 rounded-lg bg-zinc-900/60 border border-zinc-850 hover:bg-zinc-900 transition-all cursor-pointer">
                              <input 
                                type="checkbox" 
                                checked={comp.pptSubmitted} 
                                onChange={() => handleToggleCompChecklist(comp, 'pptSubmitted')}
                                className="rounded border-zinc-800 text-indigo-500 focus:ring-0 w-3.5 h-3.5 bg-zinc-950" 
                              />
                              <span className="text-xs font-semibold text-zinc-300">PPT / Slide deck</span>
                            </label>

                            <label className="flex items-center gap-2.5 p-3 rounded-lg bg-zinc-900/60 border border-zinc-850 hover:bg-zinc-900 transition-all cursor-pointer">
                              <input 
                                type="checkbox" 
                                checked={comp.reportSubmitted} 
                                onChange={() => handleToggleCompChecklist(comp, 'reportSubmitted')}
                                className="rounded border-zinc-800 text-indigo-500 focus:ring-0 w-3.5 h-3.5 bg-zinc-950" 
                              />
                              <span className="text-xs font-semibold text-zinc-300">Report Submitted</span>
                            </label>

                            <div className="flex items-center gap-2.5 p-3 rounded-lg bg-zinc-900/60 border border-zinc-850 text-zinc-400 text-xs font-semibold">
                              <Bot className="w-3.5 h-3.5 text-indigo-400" />
                              <span>Demo Link ready</span>
                            </div>

                            <div className="flex items-center gap-2.5 p-3 rounded-lg bg-zinc-900/60 border border-zinc-850 text-zinc-400 text-xs font-semibold">
                              <Activity className="w-3.5 h-3.5 text-emerald-400" />
                              <span>GitHub Linked</span>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12 text-zinc-500 text-xs">No active competitions monitored.</div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 4: PROJECTS */}
              {activeTab === 'projects' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                    <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">Active Workspace Projects</h3>
                    <form onSubmit={handleCreateProject} className="flex gap-2">
                      <input 
                        type="text" 
                        placeholder="Project name..." 
                        value={projectInput}
                        onChange={e => setProjectInput(e.target.value)}
                        className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none placeholder-zinc-600"
                      />
                      <button type="submit" className="px-3 bg-zinc-100 hover:bg-zinc-300 text-black text-xs font-semibold rounded-lg">
                        Create
                      </button>
                    </form>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {projects.length ? (
                      projects.map(proj => (
                        <div key={proj.id} className="glass-card rounded-xl p-5 border border-zinc-800 space-y-4">
                          <div className="flex items-center justify-between">
                            <h4 className="text-sm font-semibold text-zinc-200">{proj.name}</h4>
                            <span className="text-[10px] font-bold px-2 py-0.5 bg-zinc-800 text-indigo-400 border border-zinc-700 rounded-full">{proj.status}</span>
                          </div>
                          
                          <div className="space-y-1.5">
                            <div className="flex justify-between text-xs text-zinc-500">
                              <span>Development Milestone completion</span>
                              <span className="font-bold text-zinc-300">{Math.round(proj.progress)}%</span>
                            </div>
                            <div className="w-full bg-zinc-900 border border-zinc-850 h-1 rounded-full overflow-hidden">
                              <div className="bg-indigo-500 h-full rounded-full transition-all" style={{ width: `${proj.progress}%` }}></div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12 text-zinc-500 text-xs col-span-2">No active projects created.</div>
                    )}
                  </div>
                </div>
              )}

              {/* TAB 5: NOTES & SECOND BRAIN */}
              {activeTab === 'notes' && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    <div className="glass-card rounded-xl p-5 border border-zinc-800 space-y-4">
                      <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider border-b border-zinc-800/60 pb-2">Record to Second Brain</h4>
                      <form onSubmit={handleCreateNote} className="space-y-3">
                        <input 
                          type="text" 
                          placeholder="Note title..." 
                          value={noteTitleInput}
                          onChange={e => setNoteTitleInput(e.target.value)}
                          className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-xs text-zinc-200 focus:outline-none"
                        />
                        <textarea 
                          placeholder="Write thoughts or logs (markdown)..." 
                          value={noteContentInput}
                          onChange={e => setNoteContentInput(e.target.value)}
                          rows={6}
                          className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-xs text-zinc-200 focus:outline-none resize-none"
                        />
                        <button type="submit" className="w-full py-2 bg-zinc-100 hover:bg-zinc-300 text-black text-xs font-bold rounded-lg transition-all">
                          Record Entry
                        </button>
                      </form>
                    </div>

                    <div className="lg:col-span-2 space-y-4">
                      <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Entries ({notes.length})</h4>
                      
                      <div className="space-y-4">
                        {notes.length ? (
                          notes.map(note => (
                            <div key={note.id} className="p-5 rounded-xl bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700 transition-all space-y-3">
                              <div className="flex items-center justify-between">
                                <h5 className="text-sm font-semibold text-zinc-100">{note.title}</h5>
                                <button 
                                  onClick={() => handleSummarizeNote(note.id)}
                                  className="text-[10px] font-bold px-2 py-0.5 bg-zinc-800 hover:bg-zinc-700 text-indigo-400 border border-zinc-700 rounded flex items-center gap-1 transition-all"
                                >
                                  <Brain className="w-2.5 h-2.5" /> AI Summarize
                                </button>
                              </div>
                              
                              <p className="text-xs text-zinc-400 font-normal leading-relaxed whitespace-pre-wrap">{note.content}</p>
                              
                              {note.summary && (
                                <div className="p-3 bg-zinc-900 border border-zinc-850 rounded-lg text-[11px] text-zinc-400 font-semibold leading-normal flex items-start gap-2">
                                  <Bot className="w-3.5 h-3.5 text-zinc-500 mt-0.5 shrink-0" />
                                  <span>{note.summary}</span>
                                </div>
                              )}
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-12 text-zinc-500 text-xs">Second Brain database empty. Record your first log on the left.</div>
                        )}
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* TAB 6: HABITS & GOALS */}
              {activeTab === 'habits' && (
                <div className="space-y-8 animate-in fade-in duration-300">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    <div className="glass-card rounded-xl p-5 border border-zinc-800 space-y-4">
                      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                        <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Habit Trackers</h4>
                        <form onSubmit={handleCreateHabit} className="flex gap-2">
                          <input 
                            type="text" 
                            placeholder="Add habit..." 
                            value={habitInput}
                            onChange={e => setHabitInput(e.target.value)}
                            className="bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1 text-[11px] text-zinc-200 focus:outline-none"
                          />
                          <button type="submit" className="p-1 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-300 rounded">
                            <Plus className="w-3.5 h-3.5" />
                          </button>
                        </form>
                      </div>

                      <div className="space-y-3">
                        {habits.length ? (
                          habits.map(habit => (
                            <div key={habit.id} className="flex items-center justify-between p-3 rounded-lg bg-zinc-900/60 border border-zinc-850">
                              <span className="text-xs font-semibold text-zinc-200">{habit.name}</span>
                              <div className="flex items-center gap-3">
                                <span className="text-[10px] text-zinc-500 font-bold font-mono">Streak: {habit.streak} days</span>
                                <button 
                                  onClick={() => logHabitStreak(habit.id)}
                                  className="p-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 rounded transition-all"
                                >
                                  <Flame className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-6 text-zinc-500 text-xs">No habits monitored.</div>
                        )}
                      </div>
                    </div>

                    <div className="glass-card rounded-xl p-5 border border-zinc-800 space-y-4">
                      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                        <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Milestone Goals</h4>
                      </div>

                      <div className="space-y-4">
                        {goals.map(goal => (
                          <div key={goal.id} className="space-y-2">
                            <div className="flex justify-between text-xs">
                              <span className="font-semibold text-zinc-200">{goal.title}</span>
                              <span className="text-zinc-500 font-semibold">{goal.progress}%</span>
                            </div>
                            <div className="w-full bg-zinc-900 border border-zinc-850 h-1 rounded-full overflow-hidden">
                              <div className="bg-indigo-500 h-full rounded-full transition-all" style={{ width: `${goal.progress}%` }}></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* TAB 7: SYSTEM SETTINGS */}
              {activeTab === 'settings' && (
                <div className="glass-card rounded-xl p-6 border border-zinc-800 max-w-2xl space-y-6 animate-in fade-in duration-300">
                  <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider border-b border-zinc-800 pb-2">System Config</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 rounded-lg bg-zinc-900/60 border border-zinc-850">
                      <div>
                        <h4 className="text-xs font-bold text-zinc-200">Google Calendar Auth (2-Way Sync)</h4>
                        <p className="text-[10px] text-zinc-500">Authorize access for mail account anandhappriya@gmail.com</p>
                      </div>
                      <button 
                        onClick={handleConnectGoogleCalendar}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-black hover:bg-zinc-200 text-xs font-bold rounded-lg transition-all"
                      >
                        <LinkIcon className="w-3.5 h-3.5" />
                        Link Account
                      </button>
                    </div>

                    <div className="flex items-center justify-between p-4 rounded-lg bg-zinc-900/60 border border-zinc-850">
                      <div>
                        <h4 className="text-xs font-bold text-zinc-200">OpenAI API Engine</h4>
                        <p className="text-[10px] text-zinc-500">Enable advanced multi-agent workflows</p>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 bg-zinc-800 text-zinc-400 border border-zinc-700 rounded font-bold">Offline Fallback Mode</span>
                    </div>

                    <div className="flex items-center justify-between p-4 rounded-lg bg-zinc-900/60 border border-zinc-850">
                      <div>
                        <h4 className="text-xs font-bold text-zinc-200">Telegram Bot Notifications</h4>
                        <p className="text-[10px] text-zinc-500">Smart reminders on schedule conflicts</p>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 bg-zinc-800 text-zinc-400 border border-zinc-700 rounded font-bold">Config Pending</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* 3. Floating AI Assistant Pane */}
      <div className={`fixed bottom-6 right-6 z-20 transition-all duration-300 ${
        isChatOpen ? 'w-96 h-[500px]' : 'w-14 h-14'
      }`}>
        {isChatOpen ? (
          <div className="w-full h-full glass-panel border border-zinc-800/80 rounded-2xl flex flex-col overflow-hidden shadow-2xl">
            <div className="px-4 py-3 border-b border-zinc-800/60 flex items-center justify-between bg-zinc-900/80">
              <div className="flex items-center gap-2">
                <Bot className="w-4.5 h-4.5 text-zinc-100" />
                <div>
                  <h4 className="text-xs font-bold text-zinc-100 leading-none">AI Chief of Staff</h4>
                  <span className="text-[9px] text-zinc-500 font-semibold">Anandhappriya S Assistant</span>
                </div>
              </div>
              <button 
                onClick={() => setIsChatOpen(false)}
                className="text-xs text-zinc-500 hover:text-zinc-300 font-medium px-2 py-0.5 bg-zinc-800 rounded border border-zinc-750"
              >
                Hide
              </button>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-3 scrollbar-thin">
              {chatHistory.map((item, index) => (
                <div key={index} className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-xl px-3 py-2 text-xs leading-relaxed ${
                    item.role === 'user'
                      ? 'bg-zinc-100 text-black font-semibold'
                      : 'bg-zinc-900 border border-zinc-850 text-zinc-200'
                  }`}>
                    {item.text}
                  </div>
                </div>
              ))}
              {sendingChat && (
                <div className="flex justify-start">
                  <div className="bg-zinc-900 border border-zinc-850 rounded-xl px-3 py-2 text-xs text-zinc-500 flex items-center gap-1.5">
                    <RefreshCw className="w-3 h-3 animate-spin" /> Analysing workspace...
                  </div>
                </div>
              )}
              <div ref={chatEndRef}></div>
            </div>

            <form onSubmit={handleSendChat} className="p-3 border-t border-zinc-800/60 bg-zinc-900/40 flex gap-2">
              <input
                type="text"
                placeholder="Ask Chief of Staff..."
                value={chatMessage}
                onChange={e => setChatMessage(e.target.value)}
                disabled={sendingChat}
                className="flex-1 bg-zinc-955 border border-zinc-855 rounded-lg px-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none"
              />
              <button 
                type="submit" 
                disabled={sendingChat || !chatMessage.trim()}
                className="p-1.5 bg-white text-black rounded-lg hover:bg-zinc-200 transition-all shrink-0"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        ) : (
          <button 
            onClick={() => setIsChatOpen(true)}
            className="w-14 h-14 rounded-full bg-white hover:bg-zinc-200 text-black shadow-2xl flex items-center justify-center transition-transform hover:scale-105 duration-200"
          >
            <Bot className="w-6 h-6" />
          </button>
        )}
      </div>

    </div>
  );
}

const defaultBriefingText = `--- DAILY BRIEFING FOR ANANDHAPPRIYA S ---
Date: Monday, Jul 13, 2026

Tasks Due/Active Today (2):
 - [URGENT] Setup LifeOS AI Platform skeleton
 - [HIGH] Draft Competitions Review PPT

Calendar Events Today (1):
 - 22:00 - 23:59: LifeOS AI Project Setup

⚠️ Warnings & Conflicts:
 - No schedule conflicts detected. Good job!

Habits Tracking (2):
 - Code daily (Streak: 5 days)
 - Read research papers (Streak: 2 days)

Goals Tracked (1):
 - Launch LifeOS AI v1.0 (45.0% complete)`;

const mockData = {
  tasks: [
    { id: '1', title: 'Setup LifeOS AI Platform skeleton', status: 'IN_PROGRESS', priority: 'URGENT', estimatedMinutes: 60 },
    { id: '2', title: 'Draft Competitions Review PPT', status: 'TODO', priority: 'HIGH', estimatedMinutes: 45 },
    { id: '3', title: 'Verify Google Calendar sync tokens', status: 'DONE', priority: 'MEDIUM', estimatedMinutes: 20 }
  ] as Task[],

  events: [
    { id: 'e1', title: 'LifeOS AI Project Setup', description: 'Setup FastAPI backend and Next.js frontend', startTime: new Date().toISOString(), endTime: new Date(Date.now() + 7200000).toISOString() }
  ] as CalendarEvent[],

  habits: [
    { id: 'h1', name: 'Code daily', streak: 5, frequency: 'DAILY' },
    { id: 'h2', name: 'Read research papers', streak: 2, frequency: 'DAILY' }
  ] as Habit[],

  goals: [
    { id: 'g1', title: 'Launch LifeOS AI v1.0', progress: 45.0 }
  ] as Goal[],

  projects: [
    { id: 'p1', name: 'LifeOS Core Engine', description: 'FastAPI and Next.js development workspace', progress: 50.0, status: 'ACTIVE' },
    { id: 'p2', name: 'Second Brain Sync API', description: 'Supabase storage and note summarizer', progress: 20.0, status: 'ON_HOLD' }
  ] as Project[],

  competitions: [
    { id: 'c1', title: 'Global AI Productivity Hackathon', description: 'Building the ultimate LifeOS agent suite', progress: 50.0, reportSubmitted: true, pptSubmitted: true, githubUrl: 'https://github.com/anandhappriya' }
  ] as Competition[],

  notes: [
    { id: 'n1', title: 'Agentic Architectures', content: 'Multi-agent frameworks benefit from specialized node routing like LangGraph. Shared memory states are vital.', summary: 'Multi-agent workflows run best with routing states and modular node designs.', tags: ['AI', 'Architectures'] }
  ] as Note[],

  analytics: {
    completionRate: 33.3,
    focusTimeMinutes: 20,
    missedDeadlinesCount: 0,
    burnoutRisk: 'LOW',
    habitScore: 7,
    chartData: [
      { date: 'Jul 07', completed: 1, total: 3 },
      { date: 'Jul 08', completed: 2, total: 4 },
      { date: 'Jul 09', completed: 0, total: 2 },
      { date: 'Jul 10', completed: 3, total: 5 },
      { date: 'Jul 11', completed: 2, total: 3 },
      { date: 'Jul 12', completed: 1, total: 4 },
      { date: 'Jul 13', completed: 1, total: 3 }
    ]
  } as Analytics
};
