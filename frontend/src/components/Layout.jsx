import React, { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  LayoutDashboard,
  Calendar,
  GraduationCap,
  FileText,
  Megaphone,
  Briefcase,
  BookOpen,
  ClipboardList,
  Bell,
  Mail,
  LogOut,
  User,
  ChevronRight,
  Menu,
  X,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Code,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Attendance', href: '/attendance', icon: Calendar },
  { name: 'Academics', href: '/academics', icon: GraduationCap },
  { name: 'Examinations', href: '/examinations', icon: FileText },
  { name: 'Announcements', href: '/announcements', icon: Megaphone },
  { name: 'Placements', href: '/placements', icon: Briefcase },
  { name: 'Study Materials', href: '/materials', icon: BookOpen },
  { name: 'Assignments', href: '/assignments', icon: ClipboardList },
  { name: 'Coding', href: '/coding', icon: Code },
  { name: 'Reminders', href: '/reminders', icon: Bell },
  { name: 'Notifications', href: '/notifications', icon: Mail },
]

export function Layout() {
  const { user, profile, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getInitials = (name) => {
    return name ? name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'U'
  }

  const studentNav = navigation
  const teacherNav = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Students', href: '/students', icon: User },
    { name: 'Attendance', href: '/attendance', icon: Calendar },
    { name: 'Announcements', href: '/announcements', icon: Megaphone },
    { name: 'Assignments', href: '/assignments', icon: ClipboardList },
    { name: 'Coding', href: '/coding', icon: Code },
    { name: 'Placements', href: '/placements', icon: Briefcase },
    { name: 'Notifications', href: '/notifications', icon: Mail },
  ]
  const currentNav = user?.role === 'teacher' ? teacherNav : studentNav

  const displayName = user?.full_name || 'User'
  const displayId = profile?.student_id || profile?.employee_id || ''
  const displaySubtitle = profile?.department || user?.role || ''

  return (
    <div className="app-layout">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`} role="navigation" aria-label="Main navigation">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <Shield className="w-6 h-6" />
            <span>AIO Student's Hub</span>
          </div>
          <button
            className="btn-ghost btn-sm"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
            style={{ marginLeft: 'auto', display: 'none' }}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="sidebar-nav" aria-label="Primary">
          {currentNav.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
              end={item.href === '/dashboard'}
            >
              <item.icon className="w-5 h-5" aria-hidden="true" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-menu">
            <div className="user-avatar" aria-hidden="true">
              {getInitials(displayName)}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 500, color: 'var(--color-text)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {displayName}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {displaySubtitle} {displayId ? `(${displayId})` : ''}
              </div>
            </div>
            <button className="btn-ghost btn-sm" onClick={handleLogout} aria-label="Log out">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      <div className="main-content">
        <header className="header" role="banner">
          <div className="header-left">
            <button
              className="btn-ghost btn-sm"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation menu"
              style={{ display: 'none' }}
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
          <div className="header-right">
            <div className="header-action" style={{ display: 'none' }}>
              <Bell className="w-5 h-5" />
              <span>Notifications</span>
            </div>
          </div>
        </header>

        <main className="page-content" role="main">
          <Outlet />
        </main>
      </div>

      {sidebarOpen && (
        <div
          className="modal-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  )
}