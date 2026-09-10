import React, { useEffect, useState } from 'react'
import { notificationsApi } from '../services/api'
import { formatDistanceToNow } from 'date-fns'
import { Mail, AlertTriangle, Loader2, CheckCircle, Bell, Megaphone, FileText, Calendar, Briefcase, Check, Archive, RotateCcw, ClipboardList } from 'lucide-react'

const sourceIcons = {
  assignment_deadline: ClipboardList,
  reminder_trigger: Bell,
  announcement: Megaphone,
  examination: FileText,
  placement: Briefcase,
}

const sourceColors = {
  assignment_deadline: 'var(--color-primary)',
  reminder_trigger: 'var(--color-warning)',
  announcement: 'var(--color-success)',
  examination: 'var(--color-danger)',
  placement: 'var(--color-secondary)',
}

function NotificationCard({ notification, onMarkRead, onMarkUnread, loadingIds }) {
  const Icon = sourceIcons[notification.source] || Mail
  const color = sourceColors[notification.source] || 'var(--color-primary)'
  const createdAt = new Date(notification.created_at)
  const isLoading = loadingIds.has(notification.id)

  return (
    <div className={`card ${notification.status === 'unread' ? 'border-l-4' : ''}`} style={{ padding: '1.25rem', borderLeftColor: notification.status === 'unread' ? color : 'transparent', background: notification.status === 'unread' ? `${color}08` : 'var(--color-surface)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: 'var(--radius-md)', background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', color, flexShrink: 0 }}>
          <Icon className="w-5 h-5" />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', marginBottom: '0.5rem' }}>
            <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{notification.title}</h3>
            <time style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
              {formatDistanceToNow(createdAt, { addSuffix: true })}
            </time>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>{notification.message}</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color }}>
              <Icon className="w-3.5 h-3.5" />
              {notification.source.replace('_', ' ')}
            </span>
            {notification.status === 'unread' && (
              <span className="badge badge-primary" style={{ fontSize: '0.625rem' }}>New</span>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
          {notification.status === 'unread' && (
            <button
              className="btn btn-primary btn-sm"
              onClick={() => onMarkRead(notification.id)}
              disabled={isLoading}
              style={{ width: '100px' }}
            >
              <Check className="w-3.5 h-3.5" />
              Mark Read
            </button>
          )}
          {notification.status === 'read' && (
            <button
              className="btn btn-outline btn-sm"
              onClick={() => onMarkUnread(notification.id)}
              disabled={isLoading}
              style={{ width: '100px' }}
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Mark Unread
            </button>
          )}
          <button
            className="btn btn-outline btn-sm"
            onClick={() => {}} // Archive would need API
            disabled={isLoading}
            style={{ width: '100px' }}
          >
            <Archive className="w-3.5 h-3.5" />
            Archive
          </button>
        </div>
      </div>
    </div>
  )
}

export function NotificationsPage() {
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')
  const [loadingIds, setLoadingIds] = useState(new Set())

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await notificationsApi.get({ status: filter === 'all' ? undefined : filter })
        setNotifications(res.data.notifications || [])
        setUnreadCount(res.data.unread_count || 0)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [filter])

  const handleMarkRead = async (id) => {
    setLoadingIds(prev => new Set(prev).add(id))
    try {
      await notificationsApi.markRead(id)
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, status: 'read', read_at: new Date().toISOString() } : n))
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingIds(prev => { const next = new Set(prev); next.delete(id); return next })
    }
  }

  const handleMarkUnread = async (id) => {
    setLoadingIds(prev => new Set(prev).add(id))
    try {
      // No API for mark unread yet
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, status: 'unread', read_at: null } : n))
      setUnreadCount(prev => prev + 1)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingIds(prev => { const next = new Set(prev); next.delete(id); return next })
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllRead()
      setNotifications(prev => prev.map(n => ({ ...n, status: 'read', read_at: new Date().toISOString() })))
      setUnreadCount(0)
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return (
      <div className="grid grid-1">
        {[1, 2, 3].map(i => (
          <div key={i} className="card" style={{ padding: '1.25rem' }}>
            <div className="animate-pulse" style={{ display: 'flex', gap: '1rem' }}>
              <div className="animate-pulse" style={{ width: '40px', height: '40px', borderRadius: 'var(--radius-md)', background: 'var(--color-border)' }} />
              <div style={{ flex: 1 }}>
                <div className="animate-pulse" style={{ height: '1.5rem', width: '60%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)', marginBottom: '0.5rem' }} />
                <div className="animate-pulse" style={{ height: '2rem', width: '80%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)' }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle className="w-12 h-12" />
        <h3>Failed to load notifications</h3>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Notifications</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Your academic updates and alerts</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {unreadCount > 0 && (
            <button className="btn btn-primary" onClick={handleMarkAllRead}>
              <CheckCircle className="w-5 h-5" />
              <span>Mark All Read ({unreadCount})</span>
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem', overflowX: 'auto' }}>
        {['all', 'unread', 'read'].map(f => (
          <button
            key={f}
            className={`btn ${filter === f ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setFilter(f)}
            style={{ whiteSpace: 'nowrap' }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {notifications.length === 0 ? (
        <div className="empty-state">
          <Mail className="w-12 h-12" />
          <h3>No Notifications</h3>
          <p>{filter === 'all' ? 'You\'re all caught up!' : `No ${filter} notifications`}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {notifications.map(notification => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onMarkRead={handleMarkRead}
              onMarkUnread={handleMarkUnread}
              loadingIds={loadingIds}
            />
          ))}
        </div>
      )}
    </div>
  )
}