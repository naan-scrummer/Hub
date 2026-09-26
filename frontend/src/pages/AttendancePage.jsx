import React, { useEffect, useState } from 'react'
import { attendanceApi } from '../services/api'
import { format } from 'date-fns'
import { Calendar, RefreshCw, AlertTriangle, CheckCircle, Loader2, ExternalLink, Globe } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { PortalWebViewer } from '../components/PortalWebViewer'

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
  const { user } = useAuth()
  const isTeacher = user?.role === 'teacher'

  const [subjects, setSubjects] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)
  const [showPortalView, setShowPortalView] = useState(false)

  // Teacher state
  const [students, setStudents] = useState([])
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [marking, setMarking] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        if (isTeacher) {
          const res = await attendanceApi.getDailyByDate(selectedDate)
          setStudents(res.data || [])
        } else {
          // Student logic - fetch daily summary
          const dailySummaryRes = await attendanceApi.getDailySummary()

          // Fallback to legacy portal attendance if needed, but primary is daily
          const [subjectsRes, summaryRes] = await Promise.all([
            attendanceApi.getSubjects(),
            attendanceApi.getSummary(),
          ])

          setSubjects(subjectsRes.data)
          setSummary({
            ...summaryRes.data,
            daily: dailySummaryRes.data
          })
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [isTeacher, selectedDate])

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

  const handleMarkAttendance = async (studentId, status) => {
    setMarking(true)
    try {
      await attendanceApi.markDaily({
        student_id: studentId,
        date: selectedDate,
        status: status
      })
      // Update local state
      setStudents(prev => prev.map(s => s.student_id === studentId ? { ...s, status } : s))
    } catch (err) {
      alert("Failed to mark attendance: " + err.message)
    } finally {
      setMarking(false)
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

  if (isTeacher) {
    return (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Mark Daily Attendance</h1>
            <p style={{ color: 'var(--color-text-secondary)' }}>Record attendance for students</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <label style={{ fontWeight: 500 }}>Date:</label>
            <input
              type="date"
              className="form-input"
              value={selectedDate}
              onChange={e => setSelectedDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        <div className="card" style={{ padding: '0' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--color-background-soft)', borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Student ID</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Name</th>
                <th style={{ padding: '1rem', textAlign: 'center', fontWeight: 600 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {students.map(student => (
                <tr key={student.student_id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td style={{ padding: '1rem' }}>{student.student_registration_id || student.student_id}</td>
                  <td style={{ padding: '1rem' }}>{student.name}</td>
                  <td style={{ padding: '1rem', textAlign: 'center', display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
                    <button
                      className={`btn btn-sm ${student.status === 'present' ? 'btn-success' : 'btn-secondary'}`}
                      onClick={() => handleMarkAttendance(student.student_id, 'present')}
                      disabled={marking}
                    >
                      {student.status === 'present' ? 'Marked Present' : 'Present'}
                    </button>
                    <button
                      className={`btn btn-sm ${student.status === 'absent' ? 'btn-danger' : 'btn-secondary'}`}
                      onClick={() => handleMarkAttendance(student.student_id, 'absent')}
                      disabled={marking}
                    >
                      {student.status === 'absent' ? 'Marked Absent' : 'Absent'}
                    </button>
                  </td>
                </tr>
              ))}
              {students.length === 0 && (
                <tr>
                  <td colSpan="3" style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                    No students found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            className={`btn ${showPortalView ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setShowPortalView(prev => !prev)}
          >
            <Globe className="w-5 h-5" />
            <span>{showPortalView ? 'Back to Attendance' : 'Open Portal Website'}</span>
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleSync}
            disabled={syncing}
          >
            <RefreshCw className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} />
            <span>Sync from Portal</span>
          </button>
        </div>
      </div>

      {showPortalView ? (
        <PortalWebViewer defaultUrl="https://auegov.ac.in" onClose={() => setShowPortalView(false)} />
      ) : (
        <>
          {summary && (
            <>
              <div className="card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
                <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Daily Attendance (Teacher Marked)</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                  <div>
                    <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Daily Attendance</p>
                    <p style={{ fontSize: '2.5rem', fontWeight: 700, color: (summary.daily?.attendance_percentage || 0) >= 75 ? 'var(--color-success)' : (summary.daily?.attendance_percentage || 0) >= 60 ? 'var(--color-warning)' : 'var(--color-danger)' }}>
                      {(summary.daily?.attendance_percentage || 0).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontWeight: 500 }}>Classes Present</p>
                    <p style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-text)' }}>
                      {summary.daily?.present || 0} / {summary.daily?.total_classes || 0}
                    </p>
                  </div>
                </div>

                {summary.daily?.history?.length > 0 && (
                  <div style={{ marginTop: '1.5rem' }}>
                    <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Recent History</h3>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      {summary.daily.history.slice(0, 7).map(record => (
                        <span key={record.id} className={`badge ${record.status === 'PRESENT' ? 'badge-success' : 'badge-danger'}`} title={record.date}>
                          {format(new Date(record.date), 'MMM d')}: {record.status}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
                <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Portal Attendance (Legacy)</h2>
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
            </>
          )}

          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>By Subject (Portal)</h2>

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
        </>
      )}
    </div>
  )
}