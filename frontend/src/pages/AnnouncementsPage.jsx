import React, { useEffect, useState } from 'react'
import { announcementsApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import { useAuth } from '../contexts/AuthContext'
import { Megaphone, RefreshCw, AlertTriangle, Plus, X, Globe } from 'lucide-react'
import { PortalWebViewer } from '../components/PortalWebViewer'

const categories = ['all', 'examination', 'administrative', 'event', 'department', 'academic']
const createCategories = ['examination', 'administrative', 'event', 'department', 'academic']

function AnnouncementCard({ announcement }) {
  const pubDate = announcement.published_at ? new Date(announcement.published_at) : null
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
              {pubDate ? formatDistanceToNow(pubDate, { addSuffix: true }) : 'Date Unknown'}
            </time>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem', whiteSpace: 'pre-wrap' }}>{announcement.content}</p>
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
  const { user } = useAuth()
  const [announcements, setAnnouncements] = useState([])
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')
  const [showPortalView, setShowPortalView] = useState(false)

  const [isCreating, setIsCreating] = useState(false)
  const [createData, setCreateData] = useState({ title: '', content: '', category: 'academic' })
  const [creating, setCreating] = useState(false)

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

  useEffect(() => {
    fetchData()
  }, [])

  const handleSync = async (sourceId) => {
    setSyncing(true)
    setError(null)
    try {
      await announcementsApi.sync(sourceId)
      await fetchData()
    } catch (err) {
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    setCreating(true)
    setError(null)
    try {
      await announcementsApi.create(createData)
      setIsCreating(false)
      setCreateData({ title: '', content: '', category: 'academic' })
      await fetchData()
    } catch (err) {
      setError(err.message)
    } finally {
      setCreating(false)
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
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <button
            className={`btn ${showPortalView ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setShowPortalView(prev => !prev)}
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <Globe className="w-4 h-4" />
            <span>{showPortalView ? 'Back to Notices' : 'Open Portal Website'}</span>
          </button>
          {user?.role === 'teacher' && (
            <button className="btn btn-primary btn-sm" onClick={() => setIsCreating(true)}>
              <Plus className="w-4 h-4" />
              <span>New</span>
            </button>
          )}
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

      {showPortalView ? (
        <PortalWebViewer defaultUrl="https://www.annauniv.edu/" onClose={() => setShowPortalView(false)} />
      ) : (
        <>
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

          {isCreating && (
            <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem', border: '1px solid var(--color-primary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h3 style={{ fontWeight: 600 }}>Create New Announcement</h3>
                <button className="btn-ghost btn-sm" onClick={() => setIsCreating(false)}>
                  <X className="w-4 h-4" />
                </button>
              </div>
              <form onSubmit={handleCreate}>
                <div className="form-group">
                  <label className="form-label">Title</label>
                  <input required type="text" className="form-input" value={createData.title} onChange={e => setCreateData({ ...createData, title: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Category</label>
                  <select className="form-input" value={createData.category} onChange={e => setCreateData({ ...createData, category: e.target.value })}>
                    {createCategories.map(cat => <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Content</label>
                  <textarea required className="form-input" rows="4" value={createData.content} onChange={e => setCreateData({ ...createData, content: e.target.value })} />
                </div>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Publishing...' : 'Publish Announcement'}
                </button>
              </form>
            </div>
          )}

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
        </>
      )}
    </div>
  )
}