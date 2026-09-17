import React, { useEffect, useState, useRef } from 'react'
import { studyMaterialsApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import { BookOpen, Search, Filter, Plus, ExternalLink, FileText, Loader2, AlertTriangle, ChevronDown } from 'lucide-react'

const materialTypes = ['all', 'notes', 'textbook', 'practice', 'lab_manual', 'question_paper', 'reference', 'other']

function MaterialCard({ material }) {
  const typeColors = {
    notes: 'var(--color-primary)',
    textbook: 'var(--color-success)',
    practice: 'var(--color-warning)',
    lab_manual: 'var(--color-danger)',
    question_paper: 'var(--color-primary)',
    reference: 'var(--color-secondary)',
    other: 'var(--color-text-muted)',
  }
  const typeColor = typeColors[material.material_type] || 'var(--color-text-muted)'

  return (
    <div className="card" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', marginBottom: '0.75rem' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)', marginBottom: '0.25rem' }}>{material.title}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>{material.subject_code || material.subject_name || 'Unknown Subject'}</p>
        </div>
        <span className="badge" style={{ background: `${typeColor}15`, color: typeColor, fontSize: '0.6875rem' }}>
          {material.material_type.replace('_', ' ')}
        </span>
      </div>

      {material.description && (
        <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '1rem', flex: 1 }}>{material.description}</p>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: 'auto', paddingTop: '0.75rem', borderTop: '1px solid var(--color-border)' }}>
        {material.external_url && (
          <a href={material.external_url} target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
            <ExternalLink className="w-3.5 h-3.5" />
            Open
          </a>
        )}
        {material.file_path && (
          <span className="btn btn-outline btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
            <FileText className="w-3.5 h-3.5" />
            Download
          </span>
        )}
        {!material.external_url && !material.file_path && (
          <span
            className="btn btn-outline btn-sm"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              color: 'var(--color-danger)',
              borderColor: 'var(--color-danger)',
              cursor: 'not-allowed',
            }}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            Resource unavailable
          </span>
        )}
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
          {formatDistanceToNow(new Date(material.created_at), { addSuffix: true })}
        </span>
      </div>
    </div>
  )
}

export function StudyMaterialsPage() {
  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [subjectFilter, setSubjectFilter] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const formRef = useRef(null)

  const fetchMaterials = async () => {
    setLoading(true)
    try {
      const res = await studyMaterialsApi.get({
        query: searchQuery,
        material_type: typeFilter === 'all' ? undefined : typeFilter,
        subject_id: subjectFilter || undefined,
      })
      setMaterials(res.data.materials || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMaterials()
  }, [searchQuery, typeFilter, subjectFilter])

  const handleUpload = async (e) => {
    e.preventDefault()
    setUploadError(null)
    setUploading(true)
    const formData = new FormData(e.target)
    try {
      await studyMaterialsApi.create(formData)
      setShowUpload(false)
      fetchMaterials()
    } catch (err) {
      setUploadError(err.message)
    } finally {
      setUploading(false)
    }
  }

  // Need useEffect because we redefined it

  if (loading) {
    return (
      <div className="grid grid-3">
        {[1, 2, 3].map(i => (
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
        <h3>Failed to load materials</h3>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Study Materials</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Browse and access academic resources</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowUpload(true)}>
          <Plus className="w-5 h-5" />
          <span>Upload Material</span>
        </button>
      </div>

      <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div style={{ flex: 1, minWidth: '250px' }}>
            <label className="form-label">Search</label>
            <div style={{ position: 'relative' }}>
              <Search className="w-5 h-5" style={{ position: 'absolute', left: '0.875rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
              <input
                className="form-input"
                style={{ paddingLeft: '2.75rem' }}
                placeholder="Search materials..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          <div style={{ minWidth: '180px' }}>
            <label className="form-label">Type</label>
            <select className="form-input" value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
              {materialTypes.map(t => <option key={t} value={t}>{t === 'all' ? 'All Types' : t.replace('_', ' ')}</option>)}
            </select>
          </div>
          <div style={{ minWidth: '180px' }}>
            <label className="form-label">Subject</label>
            <select className="form-input" value={subjectFilter} onChange={e => setSubjectFilter(e.target.value)}>
              <option value="">All Subjects</option>
              {[
                {id: '1', code: 'CS301', name: 'Database Systems'},
                {id: '2', code: 'CS302', name: 'Computer Networks'},
                {id: '3', code: 'CS303', name: 'Operating Systems'},
                {id: '4', code: 'MA201', name: 'Discrete Mathematics'},
                {id: '5', code: 'CS304', name: 'Software Engineering'},
              ].map(s => <option key={s.id} value={s.id}>{s.code} - {s.name}</option>)}
            </select>
          </div>
        </div>
      </div>

      {materials.length === 0 ? (
        <div className="empty-state">
          <BookOpen className="w-12 h-12" />
          <h3>No Materials Found</h3>
          <p>{searchQuery || typeFilter !== 'all' ? 'Try adjusting your search or filters' : 'No study materials available yet'}</p>
        </div>
      ) : (
        <div className="grid grid-3">
          {materials.map(material => <MaterialCard key={material.id} material={material} />)}
        </div>
      )}

      {showUpload && (
        <div className="modal-overlay" onClick={() => setShowUpload(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Upload Material</h3>
              <button className="btn-ghost" onClick={() => setShowUpload(false)}>
                <ExternalLink className="w-5 h-5 rotate-90" />
              </button>
            </div>
            <form ref={formRef} onSubmit={handleUpload} className="modal-content">
              {uploadError && (
                <div style={{ padding: '0.75rem', background: 'var(--color-danger-light, #fee2e2)', color: 'var(--color-danger)', borderRadius: 'var(--radius-sm)', marginBottom: '1rem' }}>
                  {uploadError}
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Subject</label>
                <select name="subject_id" className="form-input" required>
                  <option value="">Select subject</option>
                  {[ 
                    {id: '1', code: 'CS301', name: 'Database Systems'},
                    {id: '2', code: 'CS302', name: 'Computer Networks'},
                    {id: '3', code: 'CS303', name: 'Operating Systems'},
                    {id: '4', code: 'MA201', name: 'Discrete Mathematics'},
                    {id: '5', code: 'CS304', name: 'Software Engineering'},
                  ].map(s => <option key={s.id} value={s.id}>{s.code} - {s.name}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Title</label>
                <input name="title" className="form-input" placeholder="Material title" required />
              </div>
              <div className="form-group">
                <label className="form-label">Type</label>
                <select name="material_type" className="form-input" required>
                  {materialTypes.filter(t => t !== 'all').map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea name="description" className="form-input" rows={3} placeholder="Optional description" />
              </div>
              <div className="form-group">
                <label className="form-label">File</label>
                <input type="file" name="file" className="form-input" accept=".pdf,.doc,.docx,.txt,.ppt,.pptx,.jpg,.png,.zip" />
                <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                  Or provide an external link below. Max 10MB.
                </p>
              </div>
              <div className="form-group">
                <label className="form-label">External URL</label>
                <input type="url" name="external_url" className="form-input" placeholder="https://..." />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowUpload(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={uploading}>
                  {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Upload'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}