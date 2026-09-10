import React, { useEffect, useState } from 'react'
import { announcementsApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import { Megaphone, RefreshCw, AlertTriangle, Loader2, Filter, ChevronDown } from 'lucide-react'

const categories = ['all', 'examination', 'administrative', 'event', 'department', 'academic']

function AnnouncementCard({ announcement }) {
  const pubDate = new Date(announcement.published_at)
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', flexWrap: 'wrap' }}>
        <span className="badge badge-secondary" style={{ fontSize: '0.6875rem', whiteSpace: 'nowrap' }}>
          {announcement.category}
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', marginBottom: '0.5rem' }}>
            <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{announcement.title}</h3>
            <time style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' }}>
              {formatDistanceToNow(pubDate, { addSuffix: true })}
            </time>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>{announcement.content}</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            Source: {announcement.source_name || 'Unknown'}
            {announcement.source_reference && ` • Ref: ${announcement.source_reference}`}
          </p>
        </div>
      </div>
    </div>
  )
}

export function AnnouncementsPage() {
  const [announcements, setAnnouncements] = useState([])
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [annRes, srcRes] = await Promise.all([
          announcementsApi.get(),
          announcementsApi.getSources(),
        ])
        setAnnouncements(annRes.data.announcements || [])
        setSources(srcRes.data || [])
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleSync = async (sourceId) => {
    setSyncing(true)
    setError(null)
    try {
      await announcementsApi.sync(sourceId)
      const annRes = await announcementsApi.get()
      setAnnouncements(annRes.data.announcements || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  const filteredAnnouncements = filter === 'all'
    ? announcements
    : announcements.filter(a => a.category === filter)

  if (loading) {
    return (
      <div className="grid grid-2">
        {[1, 2].map(i => (
          <div key={i} className="card" style={{ padding: '1.25rem' }}>
            <div className="animate-pulse" style={{ height: '1.5rem', width: '60%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)', marginBottom: '0.5rem' }} />
            <div className="animate-pulse" style={{ height: '2rem', width: '80%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)' }} />
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle className="w-12 h-12" />
        <h3>Failed to load announcements</h3>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Announcements</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>College notices, department updates, and events</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {sources.map(source => (
            <button
              key={source.id}
              className="btn btn-outline btn-sm"
              onClick={() => handleSync(source.id)}
              disabled={syncing}
              title={`Sync ${source.name}`}
            >
              <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {categories.map(cat => (
          <button
            key={cat}
            className={`btn ${filter === cat ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setFilter(cat)}
          >
            {cat === 'all' ? 'All' : cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {filteredAnnouncements.length === 0 ? (
        <div className="empty-state">
          <Megaphone className="w-12 h-12" />
          <h3>No Announcements</h3>
          <p>{filter === 'all' ? 'No announcements available' : `No announcements in category "${filter}"`}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {filteredAnnouncements.map(announcement => (
            <AnnouncementCard key={announcement.id} announcement={announcement} />
          ))}
        </div>
      )}
    </div>
  )
}