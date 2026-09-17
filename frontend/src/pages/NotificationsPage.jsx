import React, { useEffect, useState } from 'react'
import { notificationsService } from '../services/notificationsService'
import { formatDistanceToNow } from 'date-fns'
import {
  Mail,
  AlertTriangle,
  CheckCircle,
  Bell,
  Megaphone,
  FileText,
  Briefcase,
  Check,
  ClipboardList,
} from 'lucide-react'

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

function parseApiDate(value) {
  if (!value) return new Date(NaN)
  const timestamp = String(value)
  const hasTimezone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(timestamp)
  return new Date(hasTimezone ? timestamp : `${timestamp}Z`)
}

function NotificationCard({ notification, onMarkRead, loadingIds }) {
  const normSource = (notification.source || '').toLowerCase()
  const normStatus = (notification.status || '').toLowerCase()
  const Icon = sourceIcons[normSource] || Bell
  const color = sourceColors[normSource] || 'var(--color-primary)'
  const createdAt = parseApiDate(notification.created_at)
  const isLoading = loadingIds.has(notification.id)

  const formattedSource = normSource
    ? normSource.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
    : 'General'

  return (
    <div
      className={`card ${normStatus === 'unread' ? 'border-l-4' : ''}`}
      style={{
        padding: '1.25rem',
        borderLeftColor: normStatus === 'unread' ? color : 'transparent',
        background: normStatus === 'unread' ? `${color}08` : 'var(--color-surface)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <div
          style={{
            width: '40px',
            height: '40px',
            borderRadius: 'var(--radius-md)',
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color,
            flexShrink: 0,
          }}
        >
          <Icon className="w-5 h-5" />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              gap: '1rem',
              marginBottom: '0.5rem',
            }}
          >
            <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{notification.title}</h3>
            <time style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
              {isNaN(createdAt.getTime()) ? '' : formatDistanceToNow(createdAt, { addSuffix: true })}
            </time>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>
            {notification.message}
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color }}>
              <Icon className="w-3.5 h-3.5" />
              {formattedSource}
            </span>
            {normStatus === 'unread' && (
              <span className="badge badge-primary" style={{ fontSize: '0.625rem' }}>New</span>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
          {normStatus === 'unread' && (
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

  const fetchNotifications = async () => {
    try {
      const res = await notificationsService.getNotifications(filter)
      // res may be { notifications: [...], unread_count: 3 } or array
      if (Array.isArray(res)) {
        setNotifications(res)
        setUnreadCount(res.filter(n => (n.status || '').toLowerCase() === 'unread').length)
      } else {
        setNotifications(res.notifications || [])
        setUnreadCount(res.unread_count || 0)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    setLoading(true)
    fetchNotifications()
  }, [filter])

  const handleMarkRead = async (id) => {
    setLoadingIds(prev => new Set(prev).add(id))
    try {
      await notificationsService.markAsRead(id)
      setNotifications(prev =>
        prev.map(n =>
          n.id === id ? { ...n, status: 'read', read_at: new Date().toISOString() } : n
        )
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingIds(prev => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const handleMarkAllRead = async () => {
    try {
      await notificationsService.markAllAsRead()
      setNotifications(prev =>
        prev.map(n => ({ ...n, status: 'read', read_at: new Date().toISOString() }))
      )
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
              <div
                className="animate-pulse"
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--color-border)',
                }}
              />
              <div style={{ flex: 1 }}>
                <div
                  className="animate-pulse"
                  style={{
                    height: '1.5rem',
                    width: '60%',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--color-border)',
                    marginBottom: '0.5rem',
                  }}
                />
                <div
                  className="animate-pulse"
                  style={{
                    height: '2rem',
                    width: '80%',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--color-border)',
                  }}
                />
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

  const hasUnread = unreadCount > 0 || notifications.some(n => (n.status || '').toLowerCase() === 'unread')

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Notifications</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Your academic updates and alerts</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {hasUnread && (
            <button className="btn btn-primary" onClick={handleMarkAllRead}>
              <CheckCircle className="w-5 h-5" />
              <span>Mark All Read {unreadCount > 0 ? `(${unreadCount})` : ''}</span>
            </button>
          )}
        </div>
      </div>

      <div
        style={{
          display: 'flex',
          gap: '0.5rem',
          marginBottom: '1.5rem',
          borderBottom: '1px solid var(--color-border)',
          paddingBottom: '0.5rem',
          overflowX: 'auto',
        }}
      >
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
          <p>{filter === 'all' ? "You're all caught up!" : `No ${filter} notifications found in this view.`}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {notifications.map(notification => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onMarkRead={handleMarkRead}
              loadingIds={loadingIds}
            />
          ))}
        </div>
      )}
    </div>
  )
}
export default NotificationsPage;