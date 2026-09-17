import React, { useEffect, useState, useMemo } from 'react'
import { assignmentsApi, examinationsApi } from '../services/api'
import { remindersService } from '../services/remindersService'
import { format } from 'date-fns'
import { Bell, Plus, AlertTriangle, Clock, Calendar, CheckCircle, Trash2, Edit3, X } from 'lucide-react'

/* ------------------------------------------------------------------ */
/* Constants & helpers                                                  */
/* ------------------------------------------------------------------ */

const STATUS_CLASSES = {
  pending: 'badge-warning',
  processed: 'badge-success',
  cancelled: 'badge-secondary',
}

const STATUS_LABELS = {
  pending: 'Pending',
  processed: 'Processed',
  cancelled: 'Cancelled',
}

const TRIGGER_LABELS = {
  assignment_due: 'Assignment Due',
  examination: 'Examination',
  custom: 'Custom',
}

function formatTriggerTime(iso) {
  const d = new Date(iso)
  return format(d, 'MMM dd, yyyy - hh:mm a')
}

/* ------------------------------------------------------------------ */
/* ReminderCard                                                        */
/* ------------------------------------------------------------------ */

function ReminderCard({ reminder, onEdit, onDelete, loadingIds }) {
  const triggerTime = new Date(reminder.trigger_time)
  const isPast = triggerTime < new Date() && reminder.status === 'pending'
  const isLoading = loadingIds.has(reminder.id)
  const isCancelled = reminder.status === 'cancelled'

  // Context badge (assignment / examination / custom)
  let contextBadge = null
  if (reminder.assignment_id && reminder.assignment_title) {
    contextBadge = (
      <span className="badge badge-primary" style={{ fontSize: '0.6875rem' }}>
        Assignment: {reminder.assignment_title}
      </span>
    )
  } else if (reminder.examination_id && reminder.examination_title) {
    contextBadge = (
      <span className="badge badge-purple" style={{ fontSize: '0.6875rem', background: '#7c3aed', color: '#fff' }}>
        Examination: {reminder.examination_title}
      </span>
    )
  } else {
    contextBadge = (
      <span className="badge badge-secondary" style={{ fontSize: '0.6875rem' }}>
        Custom
      </span>
    )
  }

  return (
    <div className="card" style={{ padding: '1.25rem', opacity: isCancelled ? 0.65 : 1 }}>
      {/* Row 1: Title + Status */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{
            fontWeight: 600,
            color: 'var(--color-text)',
            textDecoration: isCancelled ? 'line-through' : 'none',
          }}>
            {reminder.title}
          </h3>
          {reminder.description && (
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
              {reminder.description}
            </p>
          )}
        </div>
        <span className={`badge ${STATUS_CLASSES[reminder.status]}`}>{STATUS_LABELS[reminder.status]}</span>
      </div>

      {/* Row 2: Meta info */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.75rem', fontSize: '0.8125rem' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--color-text-secondary)' }}>
          <Calendar className="w-3.5 h-3.5" />
          {format(new Date(reminder.trigger_time), 'MMM dd, yyyy')}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: isPast && reminder.status === 'pending' ? 'var(--color-danger)' : 'var(--color-text-secondary)' }}>
          <Clock className="w-3.5 h-3.5" />
          {format(new Date(reminder.trigger_time), 'HH:mm')}
        </span>
        {isPast && reminder.status === 'pending' && (
          <span className="badge badge-danger">Overdue</span>
        )}
        {contextBadge}
      </div>

      {/* Row 3: Actions */}
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        {reminder.status === 'pending' && (
          <>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => onEdit(reminder)}
              disabled={isLoading}
            >
              <Edit3 className="w-3.5 h-3.5" />
              Edit
            </button>
            <button
              className="btn btn-danger btn-sm"
              onClick={() => onDelete(reminder.id)}
              disabled={isLoading}
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete
            </button>
          </>
        )}
        {reminder.status !== 'pending' && (
          <button
            className="btn btn-danger btn-sm"
            onClick={() => onDelete(reminder.id)}
            disabled={isLoading}
          >
            <Trash2 className="w-3.5 h-3.5" />
            Delete
          </button>
        )}
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* ReminderFormModal — handles both Create and Edit                     */
/* ------------------------------------------------------------------ */

function ReminderFormModal({ onSubmit, onCancel, assignments, examinations, initialData }) {
  const isEdit = Boolean(initialData)

  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    description: initialData?.description || '',
    trigger_type: initialData?.trigger_type || 'custom',
    trigger_time: initialData?.trigger_time
      ? new Date(initialData.trigger_time).toISOString().slice(0, 16)
      : new Date(Date.now() + 3600000).toISOString().slice(0, 16),
    assignment_id: initialData?.assignment_id || '',
    examination_id: initialData?.examination_id || '',
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (isEdit) {
      const payload = {
        title: formData.title,
        description: formData.description || null,
        trigger_time: formData.trigger_time ? new Date(formData.trigger_time).toISOString() : undefined,
      }
      onSubmit(payload)
    } else {
      const payload = {
        title: formData.title,
        description: formData.description || null,
        trigger_type: formData.trigger_type,
        trigger_time: new Date(formData.trigger_time).toISOString(),
        assignment_id: formData.trigger_type === 'assignment_due' && formData.assignment_id ? Number(formData.assignment_id) : null,
        examination_id: formData.trigger_type === 'examination' && formData.examination_id ? Number(formData.examination_id) : null,
      }
      onSubmit(payload)
    }
  }

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '480px', width: '100%' }}>
        <div className="modal-header">
          <h3 className="modal-title">{isEdit ? 'Edit Reminder' : 'Create Reminder'}</h3>
          <button className="btn-ghost" onClick={onCancel}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="modal-content">
          <div className="form-group">
            <label className="form-label">Title</label>
            <input
              className="form-input"
              value={formData.title}
              onChange={e => setFormData({...formData, title: e.target.value})}
              placeholder="Reminder title"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-input"
              rows={2}
              value={formData.description}
              onChange={e => setFormData({...formData, description: e.target.value})}
              placeholder="Optional description"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Trigger Type</label>
            <select
              className="form-input"
              value={formData.trigger_type}
              onChange={e => setFormData({...formData, trigger_type: e.target.value})}
              required
              disabled={isEdit}
            >
              <option value="custom">Custom</option>
              <option value="assignment_due">Assignment Due</option>
              <option value="examination">Examination</option>
            </select>
          </div>
          {formData.trigger_type === 'assignment_due' && (
            <div className="form-group">
              <label className="form-label">Assignment</label>
              <select
                className="form-input"
                value={formData.assignment_id}
                onChange={e => setFormData({...formData, assignment_id: e.target.value})}
                required
                disabled={isEdit}
              >
                <option value="">Select assignment</option>
                {assignments.map(a => (
                  <option key={a.id} value={a.id}>{a.title}</option>
                ))}
              </select>
            </div>
          )}
          {formData.trigger_type === 'examination' && (
            <div className="form-group">
              <label className="form-label">Examination</label>
              <select
                className="form-input"
                value={formData.examination_id}
                onChange={e => setFormData({...formData, examination_id: e.target.value})}
                required
                disabled={isEdit}
              >
                <option value="">Select examination</option>
                {examinations.map(ex => (
                  <option key={ex.id} value={ex.id}>{ex.title}</option>
                ))}
              </select>
            </div>
          )}
          <div className="form-group">
            <label className="form-label">Trigger Date &amp; Time</label>
            <input
              type="datetime-local"
              className="form-input"
              value={formData.trigger_time}
              onChange={e => setFormData({...formData, trigger_time: e.target.value})}
              required
            />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onCancel}>Cancel</button>
            <button type="submit" className="btn btn-primary">{isEdit ? 'Save Changes' : 'Create'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Main Page                                                           */
/* ------------------------------------------------------------------ */

export function RemindersPage() {
  const [reminders, setReminders] = useState([])
  const [assignments, setAssignments] = useState([])
  const [examinations, setExaminations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('pending') // 'pending' | 'processed' | 'all'
  const [showForm, setShowForm] = useState(false)
  const [editingReminder, setEditingReminder] = useState(null)
  const [loadingIds, setLoadingIds] = useState(new Set())

  /* ---- data fetching ---- */
  const fetchData = async () => {
    try {
      const [remindersData, assignRes, examRes] = await Promise.all([
        remindersService.getReminders(),
        assignmentsApi.get(),
        examinationsApi.get(),
      ])
      setReminders(Array.isArray(remindersData) ? remindersData : [])
      setAssignments(assignRes.data?.upcoming || [])
      setExaminations(examRes.data?.examinations || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  /* ---- filtered lists ---- */
  const filteredReminders = useMemo(() => {
    if (activeTab === 'pending') return reminders.filter(r => r.status === 'pending')
    if (activeTab === 'processed') return reminders.filter(r => r.status === 'processed' || r.status === 'cancelled')
    return reminders // 'all'
  }, [reminders, activeTab])

  const pendingCount = useMemo(() => reminders.filter(r => r.status === 'pending').length, [reminders])
  const totalCount = reminders.length

  /* ---- handlers ---- */
  const handleCreate = async (data) => {
    try {
      await remindersService.createReminder(data)
      setShowForm(false)
      await fetchData()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleEdit = async (data) => {
    try {
      await remindersService.updateReminder(editingReminder.id, data)
      setEditingReminder(null)
      await fetchData()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this reminder?')) return
    setLoadingIds(prev => new Set(prev).add(id))
    try {
      await remindersService.deleteReminder(id)
      setReminders(prev => prev.filter(r => r.id !== id))
      await fetchData()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingIds(prev => { const next = new Set(prev); next.delete(id); return next })
    }
  }

  const handleProcess = async () => {
    try {
      await remindersService.processDueReminders()
      await fetchData()
    } catch (err) {
      setError(err.message)
    }
  }

  /* ---- loading state ---- */
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

  /* ---- error state ---- */
  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle className="w-12 h-12" />
        <h3>Failed to load reminders</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => { setError(null); fetchData() }} style={{ marginTop: '1rem' }}>
          Retry
        </button>
      </div>
    )
  }

  /* ---- tabs ---- */
  const tabs = [
    { key: 'pending', label: 'Upcoming', count: pendingCount },
    { key: 'processed', label: 'Processed' },
    { key: 'all', label: 'All', count: totalCount },
  ]

  /* ---- render ---- */
  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Reminders</h1>
          <span className="badge badge-secondary">{totalCount}</span>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-secondary" onClick={handleProcess}>
            <Clock className="w-5 h-5" />
            <span>Process Due</span>
          </button>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <Plus className="w-5 h-5" />
            <span>Add Reminder</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0' }}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              fontWeight: activeTab === tab.key ? 600 : 400,
              color: activeTab === tab.key ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              borderBottom: activeTab === tab.key ? '2px solid var(--color-primary)' : '2px solid transparent',
              marginBottom: '-1px',
              fontSize: '0.875rem',
            }}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span style={{ marginLeft: '0.375rem', fontSize: '0.75rem', opacity: 0.7 }}>({tab.count})</span>
            )}
          </button>
        ))}
      </div>

      {/* List */}
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
      ) : filteredReminders.length === 0 ? (
        <div className="empty-state">
          <Bell className="w-8 h-8" />
          <h3>No {activeTab === 'pending' ? 'upcoming' : activeTab} reminders</h3>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {filteredReminders.map(reminder => (
            <ReminderCard
              key={reminder.id}
              reminder={reminder}
              onEdit={setEditingReminder}
              onDelete={handleDelete}
              loadingIds={loadingIds}
            />
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showForm && (
        <ReminderFormModal
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
          assignments={assignments}
          examinations={examinations}
        />
      )}

      {/* Edit Modal */}
      {editingReminder && (
        <ReminderFormModal
          onSubmit={handleEdit}
          onCancel={() => setEditingReminder(null)}
          assignments={assignments}
          examinations={examinations}
          initialData={editingReminder}
        />
      )}
    </div>
  )
}
