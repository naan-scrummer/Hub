import React, { useEffect, useState } from 'react'
import { assignmentsApi, attendanceApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import { ClipboardList, Plus, AlertTriangle, Loader2, CheckCircle, Clock, Trash2, Edit2, ExternalLink, Calendar, BookOpen } from 'lucide-react'

const statusColors = {
  upcoming: 'badge-primary',
  overdue: 'badge-danger',
  completed: 'badge-success',
}

const statusLabels = {
  upcoming: 'Upcoming',
  overdue: 'Overdue',
  completed: 'Completed',
}

function AssignmentCard({ assignment, onUpdate, onDelete, onComplete, loadingIds }) {
  const dueDate = new Date(assignment.due_date)
  const isOverdue = assignment.status === 'overdue'
  const isLoading = loadingIds.has(assignment.id)
  const [materials, setMaterials] = useState(null)
  const [loadingMaterials, setLoadingMaterials] = useState(false)

  const handleToggleMaterials = async () => {
    if (materials) {
      setMaterials(null)
      return
    }
    setLoadingMaterials(true)
    try {
      const res = await assignmentsApi.getMaterials(assignment.id)
      setMaterials(res.data.materials || [])
    } catch (err) {
      console.error('Failed to load materials', err)
    } finally {
      setLoadingMaterials(false)
    }
  }

  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{assignment.title}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.25rem' }}>
            <ExternalLink className="w-4 h-4" />
            {assignment.subject_code || assignment.subject_name || 'Unknown Subject'}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={`badge ${statusColors[assignment.status]}`}>{statusLabels[assignment.status]}</span>
        </div>
      </div>

      {assignment.description && (
        <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>{assignment.description}</p>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: isOverdue ? 'var(--color-danger)' : 'var(--color-text-secondary)' }}>
          <Calendar className="w-4 h-4" />
          <time>{format(dueDate, 'MMM d, yyyy HH:mm')}</time>
          {isOverdue && <span className="badge badge-danger">Overdue</span>}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', marginLeft: 'auto' }}>
          {assignment.status !== 'completed' && (
            <button
              className="btn btn-success btn-sm"
              onClick={() => onComplete(assignment.id)}
              disabled={isLoading}
            >
              <CheckCircle className="w-3.5 h-3.5" />
              Complete
            </button>
          )}
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onUpdate(assignment)}
            disabled={isLoading}
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onDelete(assignment.id)}
            disabled={isLoading}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <button
            className="btn btn-outline btn-sm"
            onClick={handleToggleMaterials}
            disabled={loadingMaterials}
            title="Related Materials"
          >
            {loadingMaterials ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <BookOpen className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {materials && (
        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
          <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>Related Materials</h4>
          {materials.length === 0 ? (
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>No related materials found.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {materials.map(m => (
                <li key={m.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem', background: 'var(--color-background-alt)', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ fontSize: '0.875rem' }}>{m.title}</span>
                  {m.file_path && (
                    <a href={m.file_path} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm">
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                  {m.external_url && (
                    <a href={m.external_url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm">
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

function AssignmentForm({ assignment, onSubmit, onCancel, subjects }) {
  const [formData, setFormData] = useState({
    subject_id: assignment?.subject_id || '',
    title: assignment?.title || '',
    description: assignment?.description || '',
    due_date: assignment?.due_date ? new Date(assignment.due_date).toISOString().slice(0, 16) : '',
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">{assignment ? 'Edit Assignment' : 'Create Assignment'}</h3>
          <button className="btn-ghost" onClick={onCancel}><ExternalLink className="w-5 h-5 rotate-90" /></button>
        </div>
        <form onSubmit={handleSubmit} className="modal-content">
          <div className="form-group">
            <label className="form-label">Subject</label>
            <select className="form-input" value={formData.subject_id} onChange={e => setFormData({...formData, subject_id: e.target.value})} required>
              <option value="">Select subject</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.code} - {s.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Title</label>
            <input className="form-input" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} placeholder="Assignment title" required />
          </div>
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea className="form-input" rows={3} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} placeholder="Optional description" />
          </div>
          <div className="form-group">
            <label className="form-label">Due Date</label>
            <input type="datetime-local" className="form-input" value={formData.due_date} onChange={e => setFormData({...formData, due_date: e.target.value})} required />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onCancel}>Cancel</button>
            <button type="submit" className="btn btn-primary">{assignment ? 'Update' : 'Create'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export function AssignmentsPage() {
  const [assignments, setAssignments] = useState({ upcoming: [], overdue: [], completed: [] })
  const [subjects, setSubjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingAssignment, setEditingAssignment] = useState(null)
  const [loadingIds, setLoadingIds] = useState(new Set())
  const [activeTab, setActiveTab] = useState('upcoming')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [assignRes, subjectRes] = await Promise.all([
          assignmentsApi.get(),
          attendanceApi.getSubjects(),
        ])
        setAssignments(assignRes.data)
        setSubjects(subjectRes.data)
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
      await assignmentsApi.create(data)
      setShowForm(false)
      const res = await assignmentsApi.get()
      setAssignments(res.data)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleUpdate = async (data) => {
    try {
      await assignmentsApi.update(editingAssignment.id, data)
      setShowForm(false)
      setEditingAssignment(null)
      const res = await assignmentsApi.get()
      setAssignments(res.data)
    } catch (err) {
      setError(err.message)
    }
  }

  const handleComplete = async (id) => {
    setLoadingIds(prev => new Set(prev).add(id))
    try {
      await assignmentsApi.complete(id)
      const res = await assignmentsApi.get()
      setAssignments(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingIds(prev => { const next = new Set(prev); next.delete(id); return next })
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this assignment?')) return
    setLoadingIds(prev => new Set(prev).add(id))
    try {
      await assignmentsApi.delete(id)
      const res = await assignmentsApi.get()
      setAssignments(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoadingIds(prev => { const next = new Set(prev); next.delete(id); return next })
    }
  }

  const handleEdit = (assignment) => {
    setEditingAssignment(assignment)
    setShowForm(true)
  }

  const tabs = [
    { id: 'upcoming', label: 'Upcoming', count: assignments.upcoming?.length || 0 },
    { id: 'overdue', label: 'Overdue', count: assignments.overdue?.length || 0 },
    { id: 'completed', label: 'Completed', count: assignments.completed?.length || 0 },
  ]

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
        <h3>Failed to load assignments</h3>
        <p>{error}</p>
      </div>
    )
  }

  const currentAssignments = assignments[activeTab] || []

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Assignments</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Manage your academic tasks and deadlines</p>
        </div>
        <button className="btn btn-primary" onClick={() => { setEditingAssignment(null); setShowForm(true) }}>
          <Plus className="w-5 h-5" />
          <span>New Assignment</span>
        </button>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem', overflowX: 'auto' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-outline'} btn-sm`}
            onClick={() => setActiveTab(tab.id)}
            style={{ whiteSpace: 'nowrap' }}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {currentAssignments.length === 0 ? (
        <div className="empty-state">
          <ClipboardList className="w-12 h-12" />
          <h3>No Assignments</h3>
          <p>{activeTab === 'upcoming' ? 'No upcoming assignments' : activeTab === 'overdue' ? 'No overdue assignments' : 'No completed assignments'}</p>
          {activeTab !== 'completed' && (
            <button className="btn btn-primary" onClick={() => { setEditingAssignment(null); setShowForm(true) }} style={{ marginTop: '1rem' }}>
              <Plus className="w-5 h-5" />
              <span>Create Assignment</span>
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {currentAssignments.map(assignment => (
            <AssignmentCard
              key={assignment.id}
              assignment={assignment}
              onUpdate={handleEdit}
              onDelete={handleDelete}
              onComplete={handleComplete}
              loadingIds={loadingIds}
            />
          ))}
        </div>
      )}

      {showForm && (
        <AssignmentForm
          assignment={editingAssignment}
          onSubmit={editingAssignment ? handleUpdate : handleCreate}
          onCancel={() => { setShowForm(false); setEditingAssignment(null) }}
          subjects={subjects}
        />
      )}
    </div>
  )
}
