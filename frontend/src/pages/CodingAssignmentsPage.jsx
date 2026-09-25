import React, { useEffect, useState } from 'react'
import { assignmentsApi } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { format } from 'date-fns'
import { Code, Plus, AlertTriangle, Play, ChevronRight, X, CheckCircle, Trash2 } from 'lucide-react'

export function CodingAssignmentsPage() {
  const { user } = useAuth()
  const isTeacher = user?.role === 'teacher'
  
  const [assignments, setAssignments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [selectedAssignment, setSelectedAssignment] = useState(null)

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    difficulty: 'Easy',
    allowed_languages: 'python,javascript,c,c++,java',
    time_limit: 1.0,
    memory_limit: 128,
    max_points: 100,
    due_date: '',
    test_cases: [{ input_data: '', expected_output: '', points: 10, order_index: 0 }],
  })

  useEffect(() => {
    fetchAssignments()
  }, [])

  const fetchAssignments = async () => {
    try {
      setLoading(true)
      const res = await assignmentsApi.getCoding()
      setAssignments(res.data || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAddTestCase = () => {
    setFormData({
      ...formData,
      test_cases: [
        ...formData.test_cases,
        { input_data: '', expected_output: '', points: 10, order_index: formData.test_cases.length }
      ]
    })
  }

  const handleTestCaseChange = (index, field, value) => {
    const newTestCases = [...formData.test_cases]
    newTestCases[index][field] = field === 'points' || field === 'order_index' ? parseInt(value) || 0 : value
    setFormData({ ...formData, test_cases: newTestCases })
  }

  const handleRemoveTestCase = (index) => {
    const newTestCases = formData.test_cases.filter((_, i) => i !== index)
    setFormData({ ...formData, test_cases: newTestCases })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const dataToSubmit = {
        ...formData,
        due_date: new Date(formData.due_date).toISOString(),
      }
      await assignmentsApi.createCoding(dataToSubmit)
      setShowForm(false)
      fetchAssignments()
    } catch (err) {
      alert("Failed to create coding assignment: " + err.message)
    }
  }

  const handleDelete = async (e, id) => {
    e.stopPropagation()
    if (!window.confirm("Are you sure you want to delete this coding assignment?")) return
    try {
      await assignmentsApi.deleteCoding(id)
      fetchAssignments()
    } catch (err) {
      alert("Failed to delete assignment: " + err.message)
    }
  }

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading coding assignments...</div>
  }

  if (selectedAssignment) {
    return isTeacher ? (
      <TeacherSubmissionsView assignment={selectedAssignment} onBack={() => setSelectedAssignment(null)} />
    ) : (
      <CodingWorkspace assignment={selectedAssignment} onBack={() => setSelectedAssignment(null)} />
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Coding Assignments</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Practice programming skills</p>
        </div>
        {isTeacher && (
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <Plus className="w-5 h-5" />
            <span>Create Assignment</span>
          </button>
        )}
      </div>

      {error && (
        <div className="error-state" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle className="w-6 h-6" />
          <p>{error}</p>
        </div>
      )}

      {assignments.length === 0 ? (
        <div className="empty-state">
          <Code className="w-12 h-12" />
          <h3>No Coding Assignments</h3>
          <p>There are currently no coding assignments available.</p>
        </div>
      ) : (
        <div className="grid grid-2">
          {assignments.map(a => (
            <div key={a.id} className="card" style={{ padding: '1.25rem', cursor: 'pointer', position: 'relative' }} onClick={() => setSelectedAssignment(a)}>
              {isTeacher && (
                <button
                  className="btn-ghost btn-sm"
                  style={{ position: 'absolute', top: '1rem', right: '1rem', color: 'var(--color-danger)' }}
                  onClick={(e) => handleDelete(e, a.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingRight: isTeacher ? '2rem' : '0' }}>
                <h3 style={{ fontWeight: 600 }}>{a.title}</h3>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {a.completed_by_user && (
                    <span className="badge badge-success" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <CheckCircle className="w-3 h-3" /> Completed
                    </span>
                  )}
                  <span className={`badge ${a.difficulty === 'Easy' ? 'badge-success' : a.difficulty === 'Medium' ? 'badge-warning' : 'badge-danger'}`}>
                    {a.difficulty}
                  </span>
                </div>
              </div>
              <p style={{ marginTop: '0.5rem', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                {a.description.length > 100 ? a.description.substring(0, 100) + '...' : a.description}
              </p>
              <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                <span>Max Points: {a.max_points}</span>
                <span>Due: {format(new Date(a.due_date), 'MMM d, yyyy')}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ width: '800px', maxWidth: '90vw', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3 className="modal-title">Create Coding Assignment</h3>
              <button className="btn-ghost" onClick={() => setShowForm(false)}><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleSubmit} className="modal-content">
              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Title</label>
                  <input className="form-input" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Difficulty</label>
                  <select className="form-input" value={formData.difficulty} onChange={e => setFormData({...formData, difficulty: e.target.value})}>
                    <option value="Easy">Easy</option>
                    <option value="Medium">Medium</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
              </div>
              
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-input" rows={4} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} required />
              </div>
              
              <div className="grid grid-3">
                <div className="form-group">
                  <label className="form-label">Time Limit (s)</label>
                  <input type="number" step="0.1" className="form-input" value={formData.time_limit} onChange={e => setFormData({...formData, time_limit: parseFloat(e.target.value)})} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Memory Limit (MB)</label>
                  <input type="number" className="form-input" value={formData.memory_limit} onChange={e => setFormData({...formData, memory_limit: parseInt(e.target.value)})} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Due Date</label>
                  <input type="datetime-local" className="form-input" value={formData.due_date} onChange={e => setFormData({...formData, due_date: e.target.value})} required />
                </div>
              </div>

              <div style={{ marginTop: '1.5rem', marginBottom: '1rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h4 style={{ fontWeight: 600 }}>Test Cases</h4>
                  <button type="button" className="btn btn-outline btn-sm" onClick={handleAddTestCase}>
                    <Plus className="w-4 h-4" /> Add Test Case
                  </button>
                </div>
                
                {formData.test_cases.map((tc, idx) => (
                  <div key={idx} style={{ padding: '1rem', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: 500 }}>Test Case {idx + 1}</span>
                      {formData.test_cases.length > 1 && (
                        <button type="button" className="btn-ghost btn-sm" onClick={() => handleRemoveTestCase(idx)}>
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                    <div className="grid grid-2">
                      <div className="form-group">
                        <label className="form-label">Input Data</label>
                        <textarea className="form-input" rows={2} value={tc.input_data} onChange={e => handleTestCaseChange(idx, 'input_data', e.target.value)} required />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Expected Output</label>
                        <textarea className="form-input" rows={2} value={tc.expected_output} onChange={e => handleTestCaseChange(idx, 'expected_output', e.target.value)} required />
                      </div>
                    </div>
                    <div className="form-group" style={{ width: '150px' }}>
                      <label className="form-label">Points</label>
                      <input type="number" className="form-input" value={tc.points} onChange={e => handleTestCaseChange(idx, 'points', e.target.value)} required />
                    </div>
                  </div>
                ))}
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function CodingWorkspace({ assignment, onBack }) {
  const { user } = useAuth()
  const isTeacher = user?.role === 'teacher'
  
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  
  const handleSubmit = async () => {
    if (!code.trim()) return
    setSubmitting(true)
    try {
      const res = await assignmentsApi.submitCoding({
        assignment_id: assignment.id,
        language: language,
        source_code: code
      })
      setResult(res.data)
    } catch (err) {
      alert("Submission failed: " + err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem', gap: '1rem' }}>
        <button className="btn btn-outline btn-sm" onClick={onBack}>Back</button>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{assignment.title}</h2>
      </div>
      
      <div style={{ display: 'flex', gap: '1.5rem', flex: 1, minHeight: '600px' }}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card" style={{ padding: '1.5rem', flex: 1, overflowY: 'auto' }}>
            <h3 style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Problem Description</h3>
            <div style={{ whiteSpace: 'pre-wrap', color: 'var(--color-text-secondary)', fontSize: '0.9375rem', marginBottom: '2rem' }}>
              {assignment.description}
            </div>
            
            <h3 style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Details</h3>
            <ul style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', listStyle: 'disc', paddingLeft: '1.5rem', marginBottom: '2rem' }}>
              <li>Time Limit: {assignment.time_limit}s</li>
              <li>Memory Limit: {assignment.memory_limit}MB</li>
              <li>Allowed Languages: {assignment.allowed_languages}</li>
            </ul>

            <h3 style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Test Cases</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {assignment.test_cases?.map((tc, idx) => (
                <div key={idx} style={{ padding: '1rem', background: 'var(--color-background-soft)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                  <h4 style={{ fontWeight: 600, marginBottom: '0.5rem', fontSize: '0.875rem' }}>Example {idx + 1} ({tc.points} points)</h4>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Input:</span>
                    <pre style={{ margin: '0.25rem 0 0 0', padding: '0.5rem', background: 'var(--color-background-alt)', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem', fontFamily: 'monospace' }}>{tc.input_data}</pre>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Expected Output:</span>
                    <pre style={{ margin: '0.25rem 0 0 0', padding: '0.5rem', background: 'var(--color-background-alt)', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem', fontFamily: 'monospace' }}>{tc.expected_output}</pre>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {result && (
            <div className="card" style={{ padding: '1.5rem', borderTop: result.status === 'COMPLETED' && result.score === assignment.max_points ? '4px solid var(--color-success)' : '4px solid var(--color-danger)' }}>
              <h3 style={{ fontWeight: 600, marginBottom: '1rem' }}>Submission Result</h3>
              <div style={{ display: 'flex', gap: '2rem', marginBottom: '1rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Score</span>
                  <p style={{ fontSize: '1.25rem', fontWeight: 600 }}>{result.score} / {assignment.max_points}</p>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Passed Tests</span>
                  <p style={{ fontSize: '1.25rem', fontWeight: 600 }}>{result.passed_tests} / {result.total_tests}</p>
                </div>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {result.test_results?.map((tr, idx) => (
                  <div key={idx} style={{ padding: '0.75rem', background: 'var(--color-background-alt)', borderRadius: 'var(--radius-sm)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600 }}>Test Case {idx + 1}</span>
                      <span className={`badge ${tr.status === 'PASSED' ? 'badge-success' : 'badge-danger'}`}>{tr.status}</span>
                    </div>
                    {tr.error_message && (
                      <div style={{ marginTop: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Error Message:</span>
                        <pre style={{ margin: '0.25rem 0 0 0', padding: '0.5rem', background: 'var(--color-background-soft)', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem', fontFamily: 'monospace', color: 'var(--color-danger)', whiteSpace: 'pre-wrap' }}>
                          {tr.error_message}
                        </pre>
                      </div>
                    )}
                    {tr.status === 'FAILED' && tr.actual_output && (
                      <div style={{ marginTop: '0.5rem' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>Actual Output:</span>
                        <pre style={{ margin: '0.25rem 0 0 0', padding: '0.5rem', background: 'var(--color-background-soft)', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                          {tr.actual_output}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '1rem', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <select className="form-input" style={{ width: 'auto' }} value={language} onChange={e => setLanguage(e.target.value)}>
                <option value="python">Python 3</option>
                <option value="javascript">JavaScript (Node.js)</option>
                <option value="c">C</option>
                <option value="c++">C++</option>
                <option value="java">Java</option>
              </select>
              
              {!isTeacher && (
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {(assignment.completed_by_user || (result && result.status === 'COMPLETED' && result.score === assignment.max_points)) && (
                    <button className="btn btn-success btn-sm" disabled style={{ opacity: 1 }}>
                      <CheckCircle className="w-4 h-4" />
                      Completed
                    </button>
                  )}
                  <button className="btn btn-primary btn-sm" onClick={handleSubmit} disabled={submitting || !code.trim()}>
                    <Play className={`w-4 h-4 ${submitting ? 'animate-spin' : ''}`} />
                    {submitting ? 'Running...' : 'Submit Code'}
                  </button>
                </div>
              )}
            </div>
            
            <textarea
              style={{
                flex: 1,
                padding: '1rem',
                fontFamily: 'monospace',
                fontSize: '0.9375rem',
                border: 'none',
                resize: 'none',
                outline: 'none',
                background: 'var(--color-background-alt)',
                color: 'var(--color-text)',
              }}
              value={code}
              onChange={e => setCode(e.target.value)}
              placeholder="Write your code here..."
              spellCheck="false"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function TeacherSubmissionsView({ assignment, onBack }) {
  const [submissions, setSubmissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSubmissions = async () => {
      try {
        const res = await assignmentsApi.getCodingSubmissionsForTeacher(assignment.id)
        setSubmissions(res.data || [])
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchSubmissions()
  }, [assignment.id])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1.5rem', gap: '1rem' }}>
        <button className="btn btn-outline btn-sm" onClick={onBack}>Back</button>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{assignment.title} - Submissions</h2>
      </div>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center' }}>Loading submissions...</div>
      ) : error ? (
        <div className="error-state">
          <AlertTriangle className="w-12 h-12" />
          <p>{error}</p>
        </div>
      ) : submissions.length === 0 ? (
        <div className="empty-state">
          <Code className="w-12 h-12" />
          <h3>No Submissions Yet</h3>
          <p>No student has submitted code for this assignment.</p>
        </div>
      ) : (
        <div className="card" style={{ padding: '0' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: 'var(--color-background-soft)', borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Student ID</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Language</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Score</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Passed Tests</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Status</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600 }}>Submitted At</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--color-border)' }}>
                  <td style={{ padding: '1rem' }}>{sub.student_id}</td>
                  <td style={{ padding: '1rem' }}>{sub.language}</td>
                  <td style={{ padding: '1rem', fontWeight: 600, color: sub.score === assignment.max_points ? 'var(--color-success)' : 'var(--color-text)' }}>
                    {sub.score} / {assignment.max_points}
                  </td>
                  <td style={{ padding: '1rem' }}>{sub.passed_tests} / {sub.total_tests}</td>
                  <td style={{ padding: '1rem' }}>
                    <span className={`badge ${sub.status === 'COMPLETED' ? 'badge-success' : sub.status === 'ERROR' ? 'badge-danger' : 'badge-warning'}`}>
                      {sub.status}
                    </span>
                  </td>
                  <td style={{ padding: '1rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                    {format(new Date(sub.created_at), 'MMM d, yyyy h:mm a')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
