import React, { useEffect, useState } from 'react'
import { examinationsApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import { FileText, RefreshCw, AlertTriangle, Calendar, Loader2, Clock } from 'lucide-react'

function ExamCard({ exam }) {
  const examDate = new Date(exam.exam_date)
  const daysUntil = Math.ceil((examDate - new Date()) / (1000 * 60 * 60 * 24))
  const isPast = daysUntil < 0
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
            <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{exam.title}</h3>
            <span className="badge badge-primary">{exam.exam_type}</span>
            {exam.is_unavailable && (
              <span className="badge badge-warning" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                <AlertTriangle className="w-3 h-3" />
                Unavailable
              </span>
            )}
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>{exam.subject_code || exam.subject_name || 'Unknown Subject'}</p>
          {exam.venue && (
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <ExternalLink className="w-4 h-4" />
              {exam.venue}
            </p>
          )}
        </div>
        <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
          <p style={{ fontSize: '1.125rem', fontWeight: 600, color: isPast ? 'var(--color-danger)' : 'var(--color-text)' }}>
            {isPast ? 'Past' : `${daysUntil} days`}
          </p>
          <time style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
            {format(examDate, 'MMM d, yyyy')}
          </time>
          {exam.start_time && (
            <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginTop: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem', justifyContent: 'flex-end' }}>
              <Clock className="w-3.5 h-3.5" />
              {format(new Date(exam.start_time), 'HH:mm')} - {exam.end_time ? format(new Date(exam.end_time), 'HH:mm') : '—'}
            </p>
          )}
        </div>
      </div>
      {exam.description && (
        <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
          {exam.description}
        </p>
      )}
    </div>
  )
}

export function ExaminationsPage() {
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await examinationsApi.get()
        setExams(res.data.examinations || [])
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
      await examinationsApi.sync()
      const res = await examinationsApi.get()
      setExams(res.data.examinations || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  if (loading) {
    return (
      <div className="grid grid-2">
        {[1, 2].map(i => (
          <div key={i} className="card" style={{ padding: '1.25rem' }}>
            <div className="animate-pulse" style={{ height: '1.5rem', width: '60%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)', marginBottom: '0.5rem' }} />
            <div className="animate-pulse" style={{ height: '1rem', width: '40%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)' }} />
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle className="w-12 h-12" />
        <h3>Failed to load examinations</h3>
        <p>{error}</p>
      </div>
    )
  }

  const upcoming = exams.filter(e => new Date(e.exam_date) >= new Date()).sort((a, b) => new Date(a.exam_date) - new Date(b.exam_date))
  const past = exams.filter(e => new Date(e.exam_date) < new Date()).sort((a, b) => new Date(b.exam_date) - new Date(a.exam_date))

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Examinations</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>View your exam schedule and dates</p>
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

      {exams.length === 0 ? (
        <div className="unavailable-state">
          <FileText className="w-12 h-12" />
          <h3>No Examination Data</h3>
          <p>Examination data is unavailable. Please sync from the college portal to fetch the latest schedule.</p>
          <button className="btn btn-primary" onClick={handleSync} disabled={syncing} style={{ marginTop: '1rem' }}>
            <RefreshCw className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} />
            <span>Sync from Portal</span>
          </button>
        </div>
      ) : (
        <>
          {upcoming.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Calendar className="w-5 h-5" />
                Upcoming Examinations ({upcoming.length})
              </h2>
              <div className="grid grid-2">
                {upcoming.map(exam => <ExamCard key={exam.id} exam={exam} />)}
              </div>
            </div>
          )}

          {past.length > 0 && (
            <div>
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock className="w-5 h-5" />
                Past Examinations ({past.length})
              </h2>
              <div className="grid grid-2">
                {past.map(exam => <ExamCard key={exam.id} exam={exam} />)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}