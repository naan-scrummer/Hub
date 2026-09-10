import React, { useEffect, useState } from 'react'
import { attendanceApi } from '../services/api'
import { format } from 'date-fns'
import { Calendar, RefreshCw, AlertTriangle, CheckCircle, Loader2, ExternalLink } from 'lucide-react'

function AttendanceCard({ record }) {
  const percentage = record.attendance_percentage
  const color = percentage >= 75 ? 'var(--color-success)' : percentage >= 60 ? 'var(--color-warning)' : 'var(--color-danger)'
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)', marginBottom: '0.25rem' }}>{record.subject_name || record.subject_code || 'Unknown Subject'}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>{record.classes_attended} / {record.total_classes} classes attended</p>
          {record.is_unavailable && (
            <span className="badge badge-warning" style={{ marginTop: '0.5rem', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
              <AlertTriangle className="w-3 h-3" />
              Data unavailable - sync required
            </span>
          )}
        </div>
        <div style={{ textAlign: 'right' }}>
          <p style={{ fontSize: '2rem', fontWeight: 700, color }}>{percentage.toFixed(1)}%</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            {record.last_synced_at ? `Last synced: ${format(new Date(record.last_synced_at), 'MMM d, yyyy')}` : 'Never synced'}
          </p>
        </div>
      </div>
      <div style={{ marginTop: '1rem', height: '8px', background: 'var(--color-border)', borderRadius: '4px', overflow: 'hidden' }}>
        <div style={{ width: `${Math.min(percentage, 100)}%`, height: '100%', background: color, borderRadius: '4px', transition: 'width 0.3s ease' }} />
      </div>
    </div>
  )
}

export function AttendancePage() {
  const [subjects, setSubjects] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [subjectsRes, summaryRes] = await Promise.all([
          attendanceApi.getSubjects(),
          attendanceApi.getSummary(),
        ])
        setSubjects(subjectsRes.data)
        setSummary(summaryRes.data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleSync = async () => {
    setSyncing(true)
    setError(null)
    try {
      await attendanceApi.sync(1)
      const summaryRes = await attendanceApi.getSummary()
      setSummary(summaryRes.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  if (loading) {
    return (
      <div className="grid grid-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="card" style={{ padding: '1.25rem' }}>
            <div className="animate-pulse" style={{ height: '1.5rem', width: '40%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)', marginBottom: '1rem' }} />
            <div className="animate-pulse" style={{ height: '2rem', width: '60%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)' }} />
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle className="w-12 h-12" />
        <h3>Failed to load attendance</h3>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Attendance</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Track your class attendance by subject</p>
        </div>
        <button
          className="btn btn-secondary"
          onClick={handleSync}
          disabled={syncing}
        >
          <RefreshCw className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} />
          <span>Sync from Portal</span>
        </button>
      </div>

      {summary && (
        <div className="card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Overall Attendance</p>
              <p style={{ fontSize: '2.5rem', fontWeight: 700, color: summary.overall_percentage >= 75 ? 'var(--color-success)' : summary.overall_percentage >= 60 ? 'var(--color-warning)' : 'var(--color-danger)' }}>
                {summary.overall_percentage.toFixed(1)}%
              </p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Classes Attended</p>
              <p style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-text)' }}>
                {summary.total_classes_attended} / {summary.total_classes}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Subjects Tracked</p>
              <p style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-text)' }}>
                {summary.subjects_count}
              </p>
            </div>
          </div>
        </div>
      )}

      <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>By Subject</h2>

      {summary?.records?.length === 0 && !error ? (
        <div className="unavailable-state">
          <AlertTriangle className="w-12 h-12" />
          <h3>No Attendance Data</h3>
          <p>Attendance data is unavailable. Please sync from the college portal to fetch the latest records.</p>
          <button className="btn btn-primary" onClick={handleSync} disabled={syncing} style={{ marginTop: '1rem' }}>
            <RefreshCw className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} />
            <span>Sync from Portal</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-3">
          {summary?.records?.map(record => (
            <AttendanceCard key={record.id} record={record} />
          ))}
        </div>
      )}
    </div>
  )
}