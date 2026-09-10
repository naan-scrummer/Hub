import React, { useEffect, useState } from 'react'
import { remindersApi, assignmentsApi, examinationsApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import { Bell, Plus, AlertTriangle, Loader2, Clock, Calendar, CheckCircle, Trash2, ExternalLink } from 'lucide-react'

const statusColors = {
  pending: 'badge-warning',
  processed: 'badge-success',
  cancelled: 'badge-secondary',
}

const statusLabels = {
  pending: 'Pending',
  processed: 'Processed',
  cancelled: 'Cancelled',
}

const triggerTypeLabels = {
  assignment_due: 'Assignment Due',
  examination: 'Examination',
  custom: 'Custom',
}

function ReminderCard({ reminder, onDelete, loadingIds }) {
  const triggerTime = new Date(reminder.trigger_time)
  const isPast = reminder.trigger_time < new Date().toISOString() && reminder.status === 'pending'
  const isLoading = loadingIds.has(reminder.id)

  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{reminder.title}</h3>
          {reminder.description && (
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>{reminder.description}</p>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={`badge ${statusColors[reminder.status]}`}>{statusLabels[reminder.status]}</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '0.75rem', fontSize: '0.8125rem' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-text-secondary)' }}>
          <Calendar className="w-3.5 h-3.5" />
          {format(triggerTime, 'MMM d, yyyy')}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: isPast && reminder.status === 'pending' ? 'var(--color-danger)' : 'var(--color-text-secondary)' }}>
          <Clock className="w-3.5 h-3.5" />
          {format(triggerTime, 'HH:mm')}
        </span>
        <span className={`badge ${reminder.status === 'pending' && isPast ? 'badge-danger' : statusColors[reminder.status]}`}>
          {reminder.status === 'pending' && isPast ? 'Overdue' : statusLabels[reminder.status]}
        </span>
        <span className="badge badge-secondary" style={{ fontSize: '0.6875rem' }}>
          {triggerTypeLabels[reminder.trigger_type] || reminder.trigger_type}
        </span>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginLeft: 'auto' }}>
        {reminder.status === 'pending' && (
          <button
            className="btn btn-danger btn-sm"
            onClick={() => onDelete(reminder.id)}
            disabled={loadingIds.has(reminder.id)}
          >
            <Trash2 className="w-3.5 h-3.5" />
            Delete
          </button>
        )}
      </div>
    </div>
  )
}

function ReminderForm({ onSubmit, onCancel, assignments, examinations }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    trigger_type: 'custom',
    trigger_time: new Date(Date.now() + 3600000).toISOString().slice(0, 16),
    assignment_id: '',
    examination_id: '',
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Create Reminder</h3>
          <button className="btn-ghost" onClick={onCancel}><ExternalLink className="w-5 h-5 rotate-90" /></button>
        </div>
        <form onSubmit={handleSubmit} className="modal-content">
          <div className="form-group">
            <label className="form-label">Title</label>
            <input className="form-input" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} placeholder="Reminder title" required />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-input" rows={2} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} placeholder="Optional description" />
          </div>
          <div className="form-group">
            <label className="form-label">Trigger Type</label>
            <select className="form-input" value={formData.trigger_type} onChange={e => setFormData({...formData, trigger_type: e.target.value})} required>
              <option value="custom">Custom</option>
              <option value="assignment_due">Assignment Due</option>
              <option value="examination">Examination</option>
            </select>
          </div>
          {(formData.trigger_type === 'assignment_due' || formData.trigger_type === 'examination') && (
            <>
              {formData.trigger_type === 'assignment_due' && (
                <div className="form-group">
                  <label className="form-label">Assignment</label>
                  <select className="form-input" value={formData.assignment_id} onChange={e => setFormData({...formData, assignment_id: e.target.value})} required>
                    <option value="">Select assignment</option>
                    {assignments.map(a => <option key={a.id} value={a.id}>{a.title} ({a.subject_code})</option>)}
                  </select>
                </div>
              )}
              {formData.trigger_type === 'examination' && (
                <div className="form-group">
                  <label className="form-label">Examination</label>
                  <select className="form-input" value={formData.examination_id} onChange={e => setFormData({...formData, examination_id: e.target.value})} required>
                    <option value="">Select examination</option>
                    {examinations.map(e => <option key={e.id} value={e.id}>{e.title} ({e.subject_code})</option>)}
                  </select>
                </div>
              )}
            </>
          )}
          {(formData.trigger_type === 'custom') && (
            <div className="form-group">
              <label className="form-label">Trigger Time</label>
              <input type="datetime-local" className="form-input" value={formData.trigger_time} onChange={e => setFormData({...formData, trigger_time: e.target.value})} required />
            </div>
          )}
          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onCancel}>Cancel</button>
            <button type="submit" className="btn btn-primary">Create</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export function RemindersPage() {
  const [reminders, setReminders] = useState([])
  const [assignments, setAssignments] = useState([])
  const [examinations, setExaminations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [loadingIds, setLoadingIds] = useState(new Set())

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [remRes, assignRes, examRes] = await Promise.all([
          remindersApi.get(),
          assignmentsApi.get(),
          examinationsApi.get(),
        ])
        setReminders(remRes.data || [])
        setAssignments(assignRes.data.upcoming || [])
        setExaminations(examRes.data.examinations || [])
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleCreate = async (data) => {
    try {
      await remindersApi.create(data)
      setShowForm(false)
      const res = await remindersApi.get()
      setReminders(res.data || [])
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this reminder?')) return
    setLoadingIds(prev => new Set(prev).add(id))
    try {
      // Note: No delete endpoint in API yet, would need to be added
      setReminders(prev => prev.filter(r => r.id !== id))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingIds(prev => { const next = new Set(prev); next.delete(id); return next })
    }
  }

  const handleProcess = async () => {
    try {
      await remindersApi.process()
      const res = await remindersApi.get()
      setReminders(res.data || [])
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return (
      <div className="grid grid-2">
        {[1, 2].map(i => (
          <div key={i} className="card" style={{ padding: '1.25rem' }}>
            <div className="animate-pulse" style={{ height: '1.5rem', width: '60%', borderRadius: 'var(--radius-sm)', background: 'var(--color-border)', marginBottom: '1rem' }} />
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
        <h3>Failed to load reminders</h3>
        <p>{error}</p>
      </div>
    )
  }

  const pending = reminders.filter(r => r.status === 'pending').sort((a, b) => new Date(a.trigger_time) - new Date(b.trigger_time))
  const processed = reminders.filter(r => r.status === 'processed').sort((a, b) => new Date(b.processed_at) - new Date(a.processed_at))
  const cancelled = reminders.filter(r => r.status === 'cancelled')

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Reminders</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Manage your time-sensitive reminders</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-secondary" onClick={handleProcess}>
            <Clock className="w-5 h-5" />
            <span>Process Due</span>
          </button>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <Plus className="w-5 h-5" />
            <span>New Reminder</span>
          </button>
        </div>
      </div>

      {reminders.length === 0 ? (
        <div className="empty-state">
          <Bell className="w-12 h-12" />
          <h3>No Reminders</h3>
          <p>Create your first reminder to get started</p>
          <button className="btn btn-primary" onClick={() => setShowForm(true)} style={{ marginTop: '1rem' }}>
            <Plus className="w-5 h-5" />
            <span>Create Reminder</span>
          </button>
        </div>
      ) : (
        <>
          {pending.length > 0 && (
            <div style={{ marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock className="w-5 h-5" />
                Pending Reminders ({pending.length})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {pending.map(reminder => (
                  <ReminderCard key={reminder.id} reminder={reminder} onDelete={handleDelete} loadingIds={loadingIds} />
                ))}
              </div>
            </div>
          )}

          {(processed.length > 0 || cancelled.length > 0) && (
            <div>
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckCircle className="w-5 h-5" />
                Processed & Cancelled ({processed.length + cancelled.length})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {[...processed, ...cancelled].map(reminder => (
                  <ReminderCard key={reminder.id} reminder={reminder} onDelete={handleDelete} loadingIds={loadingIds} />
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {showForm && (
        <ReminderForm
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
          assignments={assignments}
          examinations={examinations}
        />
      )}
    </div>
  )
}