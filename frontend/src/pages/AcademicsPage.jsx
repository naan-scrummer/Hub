import React, { useEffect, useState } from 'react'
import { academicsApi } from '../services/api'
import { format } from 'date-fns'
import { GraduationCap, RefreshCw, AlertTriangle, Loader2, Award } from 'lucide-react'

const gradeColors = {
  'A+': 'var(--color-success)',
  'A': 'var(--color-success)',
  'B+': 'var(--color-primary)',
  'B': 'var(--color-primary)',
  'C': 'var(--color-warning)',
  'F': 'var(--color-danger)',
  'N/A': 'var(--color-text-muted)',
}

function AcademicCard({ record }) {
  const gradeColor = gradeColors[record.grade] || 'var(--color-text)'
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)', marginBottom: '0.25rem' }}>{record.subject_name || record.subject_code || 'Unknown Subject'}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Semester {record.semester}</p>
          {record.is_unavailable && (
            <span className="badge badge-warning" style={{ marginTop: '0.5rem', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
              <AlertTriangle className="w-3 h-3" />
              Data unavailable - sync required
            </span>
          )}
        </div>
        <div style={{ textAlign: 'right' }}>
          <span className="badge" style={{ background: `${gradeColor}15`, color: gradeColor, fontSize: '1rem', padding: '0.5rem 1rem' }}>
            {record.grade || '—'}
          </span>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
            {record.total_marks !== null ? `${record.total_marks} / ${(record.max_internal_marks || 0) + (record.max_external_marks || 0)}` : '—'}
          </p>
        </div>
      </div>
      <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', fontSize: '0.8125rem' }}>
        <div>
          <p style={{ color: 'var(--color-text-secondary)' }}>Internal Marks</p>
          <p style={{ fontWeight: 500 }}>{record.internal_marks !== null ? `${record.internal_marks} / ${record.max_internal_marks}` : '—'}</p>
        </div>
        <div>
          <p style={{ color: 'var(--color-text-secondary)' }}>External Marks</p>
          <p style={{ fontWeight: 500 }}>{record.external_marks !== null ? `${record.external_marks} / ${record.max_external_marks}` : '—'}</p>
        </div>
      </div>
    </div>
  )
}

export function AcademicsPage() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await academicsApi.get()
        setRecords(res.data.records || [])
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
      await academicsApi.sync(1)
      const res = await academicsApi.get()
      setRecords(res.data.records || [])
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
        <h3>Failed to load academics</h3>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Academics</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>View your academic records and performance</p>
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

      {records.length === 0 ? (
        <div className="unavailable-state">
          <GraduationCap className="w-12 h-12" />
          <h3>No Academic Records</h3>
          <p>Academic data is unavailable. Please sync from the college portal to fetch the latest records.</p>
          <button className="btn btn-primary" onClick={handleSync} disabled={syncing} style={{ marginTop: '1rem' }}>
            <RefreshCw className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} />
            <span>Sync from Portal</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-3">
          {records.map(record => (
            <AcademicCard key={record.id} record={record} />
          ))}
        </div>
      )}
    </div>
  )
}