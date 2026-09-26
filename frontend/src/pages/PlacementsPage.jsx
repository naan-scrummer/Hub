import React, { useEffect, useState } from 'react'
import { placementsApi } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { format, formatDistanceToNow } from 'date-fns'
import { Briefcase, RefreshCw, AlertTriangle, Loader2, Plus, ExternalLink, Building, MapPin, DollarSign, Calendar, X, CheckCircle, Globe } from 'lucide-react'
import { PortalWebViewer } from '../components/PortalWebViewer'

function OpportunityCard({ opportunity }) {
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        <div>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{opportunity.title}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.25rem' }}>
            <Building className="w-4 h-4" />
            {opportunity.company_name || 'Unknown Company'}
          </p>
        </div>
        {opportunity.package_details && (
          <span className="badge badge-success" style={{ fontSize: '0.8125rem', padding: '0.375rem 0.75rem' }}>
            <DollarSign className="w-3.5 h-3.5" />
            {opportunity.package_details}
          </span>
        )}
      </div>

      {opportunity.description && (
        <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.75rem' }}>{opportunity.description}</p>
      )}

      {opportunity.eligibility_criteria && (
        <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <AlertTriangle className="w-3.5 h-3.5" />
          Eligibility: {opportunity.eligibility_criteria}
        </p>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
        {opportunity.location && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <MapPin className="w-3.5 h-3.5" />
            {opportunity.location}
          </span>
        )}
        {opportunity.application_deadline && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: new Date(opportunity.application_deadline) < new Date() ? 'var(--color-danger)' : 'var(--color-text-secondary)' }}>
            <Calendar className="w-3.5 h-3.5" />
            Apply by {format(new Date(opportunity.application_deadline), 'MMM d, yyyy')}
          </span>
        )}
        <span className={`badge ${opportunity.recruitment_status === 'open' ? 'badge-success' : 'badge-secondary'}`}>
          {opportunity.recruitment_status}
        </span>
      </div>
    </div>
  )
}

function ContributionCard({ contribution, isMine, onResubmit }) {
  const getStatusBadge = () => {
    if (contribution.status === 'APPROVED') return <span className="badge badge-success">Approved</span>
    if (contribution.status === 'REJECTED') return <span className="badge badge-danger">Rejected</span>
    if (contribution.status === 'PENDING') return <span className="badge badge-warning">Pending Review</span>
    return <span className="badge badge-secondary">{contribution.is_published ? 'Published' : 'Draft'}</span>
  }

  return (
    <div className="card" style={{ padding: '1.25rem', borderLeft: contribution.status === 'REJECTED' ? '4px solid var(--color-danger)' : 'none' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        <div>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{contribution.title}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
            {contribution.contribution_type} • {contribution.company_name || 'Unknown Company'}
          </p>
        </div>
        {getStatusBadge()}
      </div>
      <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>{contribution.content}</p>

      {contribution.status === 'REJECTED' && contribution.rejection_reason && (
        <div style={{ padding: '0.75rem', backgroundColor: 'var(--color-background-soft)', borderRadius: 'var(--radius-sm)', marginBottom: '0.75rem' }}>
          <p style={{ fontSize: '0.8125rem', color: 'var(--color-danger)', fontWeight: 500, marginBottom: '0.25rem' }}>Rejection Reason:</p>
          <p style={{ fontSize: '0.8125rem', color: 'var(--color-text)' }}>{contribution.rejection_reason}</p>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
          {formatDistanceToNow(new Date(contribution.created_at), { addSuffix: true })}
        </p>
        {isMine && contribution.status === 'REJECTED' && onResubmit && (
          <button className="btn btn-outline btn-sm" onClick={() => onResubmit(contribution)}>
            Edit & Resubmit
          </button>
        )}
      </div>
    </div>
  )
}

export function PlacementsPage() {
  const { user } = useAuth()
  const isTeacher = user?.role === 'teacher'

  const [opportunities, setOpportunities] = useState([])
  const [contributions, setContributions] = useState([])
  const [myContributions, setMyContributions] = useState([])
  const [pendingContributions, setPendingContributions] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [activeTab, setActiveTab] = useState('opportunities')
  const [showContributionForm, setShowContributionForm] = useState(false)
  const [editingContributionId, setEditingContributionId] = useState(null)
  const [error, setError] = useState(null)
  const [showPortalView, setShowPortalView] = useState(false)

  // For teacher review form
  const [reviewForm, setReviewForm] = useState({ show: false, contributionId: null, status: 'APPROVED', reason: '' })

  const [formData, setFormData] = useState({
    company_id: '',
    title: '',
    content: '',
    contribution_type: 'interview_experience',
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        const promises = [
          placementsApi.getOpportunities(),
          placementsApi.getContributions(),
        ]

        if (!isTeacher) {
          promises.push(placementsApi.getMyContributions())
        } else {
          promises.push(placementsApi.getPendingContributions())
        }

        const results = await Promise.all(promises)
        setOpportunities(results[0].data.opportunities || [])
        setContributions(results[1].data.contributions || [])

        if (!isTeacher) {
          setMyContributions(results[2].data.contributions || [])
        } else {
          setPendingContributions(results[2].data.contributions || [])
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [isTeacher])

  const handleSync = async () => {
    setSyncing(true)
    setError(null)
    try {
      await placementsApi.sync()
      const oppRes = await placementsApi.getOpportunities()
      setOpportunities(oppRes.data.opportunities || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  const handleResubmit = (contribution) => {
    setEditingContributionId(contribution.id)
    setFormData({
      company_id: contribution.company_id || '',
      title: contribution.title,
      content: contribution.content,
      contribution_type: contribution.contribution_type,
    })
    setShowContributionForm(true)
  }

  const handleSubmitContribution = async (e) => {
    e.preventDefault()
    try {
      if (editingContributionId) {
        await placementsApi.updateContribution(editingContributionId, formData)
      } else {
        await placementsApi.createContribution(formData)
      }
      setShowContributionForm(false)
      setEditingContributionId(null)
      setFormData({ company_id: '', title: '', content: '', contribution_type: 'interview_experience' })
      const myContribRes = await placementsApi.getMyContributions()
      setMyContributions(myContribRes.data.contributions || [])
    } catch (err) {
      setError(err.message)
    }
  }

  const handleReviewSubmit = async (e) => {
    e.preventDefault()
    try {
      await placementsApi.reviewContribution(reviewForm.contributionId, {
        status: reviewForm.status,
        rejection_reason: reviewForm.status === 'REJECTED' ? reviewForm.reason : null
      })
      setReviewForm({ show: false, contributionId: null, status: 'APPROVED', reason: '' })

      // Refresh pending list
      const pendingRes = await placementsApi.getPendingContributions()
      setPendingContributions(pendingRes.data.contributions || [])

      // Refresh published list
      const contribRes = await placementsApi.getContributions()
      setContributions(contribRes.data.contributions || [])
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
        <h3>Failed to load placements</h3>
        <p>{error}</p>
      </div>
    )
  }

  const tabs = [
    { id: 'opportunities', label: 'Opportunities', count: opportunities.length, icon: Briefcase },
    { id: 'contributions', label: 'Contributions', count: contributions.length, icon: Building },
  ]

  if (isTeacher) {
    tabs.push({ id: 'pending-contributions', label: 'Review Pending', count: pendingContributions.length, icon: AlertTriangle })
  } else {
    tabs.push({ id: 'my-contributions', label: 'My Contributions', count: myContributions.length, icon: Plus })
  }
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Placements</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Career opportunities and peer contributions</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            className={`btn ${showPortalView ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setShowPortalView(prev => !prev)}
          >
            <Globe className="w-5 h-5" />
            <span>{showPortalView ? 'Back to Placements' : 'Open Portal Website'}</span>
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
        <PortalWebViewer defaultUrl="https://cuic.annauniv.edu/login/student" onClose={() => setShowPortalView(false)} />
      ) : (
        <>
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.5rem', overflowX: 'auto' }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-outline'} btn-sm`}
                onClick={() => setActiveTab(tab.id)}
                style={{ whiteSpace: 'nowrap' }}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label} ({tab.count})
              </button>
            ))}
          </div>

          {activeTab === 'opportunities' && (
            <div>
              {opportunities.length === 0 ? (
                <div className="unavailable-state">
                  <Briefcase className="w-12 h-12" />
                  <h3>No Opportunities</h3>
                  <p>No placement opportunities available. Sync from portal to fetch latest data.</p>
                  <button className="btn btn-primary" onClick={handleSync} disabled={syncing} style={{ marginTop: '1rem' }}>
                    <RefreshCw className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} />
                    <span>Sync from Portal</span>
                  </button>
                </div>
              ) : (
                <div className="grid grid-2">
                  {opportunities.map(opp => <OpportunityCard key={opp.id} opportunity={opp} />)}
                </div>
              )}
            </div>
          )}

          {activeTab === 'contributions' && (
            <div>
              {contributions.length === 0 ? (
                <div className="empty-state">
                  <Building className="w-12 h-12" />
                  <h3>No Contributions</h3>
                  <p>No peer contributions available yet.</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {contributions.map(c => <ContributionCard key={c.id} contribution={c} />)}
                </div>
              )}
            </div>
          )}

          {activeTab === 'my-contributions' && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>My Contributions</h2>
                <button className="btn btn-primary btn-sm" onClick={() => setShowContributionForm(true)}>
                  <Plus className="w-4 h-4" />
                  Add Contribution
                </button>
              </div>

              {showContributionForm && (
                <div className="modal-overlay" onClick={() => setShowContributionForm(false)}>
                  <div className="modal" onClick={e => e.stopPropagation()}>
                    <div className="modal-header">
                      <h3 className="modal-title">Add Contribution</h3>
                      <button className="btn-ghost" onClick={() => setShowContributionForm(false)}><ExternalLink className="w-5 h-5 rotate-90" /></button>
                    </div>
                    <form onSubmit={handleSubmitContribution} className="modal-content">
                      <div className="form-group">
                        <label className="form-label">Company</label>
                        <select className="form-input" value={formData.company_id} onChange={e => setFormData({ ...formData, company_id: e.target.value })} required>
                          <option value="">Select company</option>
                          {[
                            { id: '1', name: 'TechCorp Solutions' },
                            { id: '2', name: 'DataFlow Analytics' },
                            { id: '3', name: 'CloudNine Systems' },
                          ].map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label">Type</label>
                        <select className="form-input" value={formData.contribution_type} onChange={e => setFormData({ ...formData, contribution_type: e.target.value })} required>
                          <option value="interview_experience">Interview Experience</option>
                          <option value="preparation_resource">Preparation Resource</option>
                          <option value="tips">Tips & Advice</option>
                        </select>
                      </div>
                      <div className="form-group">
                        <label className="form-label">Title</label>
                        <input className="form-input" value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })} placeholder="e.g., My TechCorp Interview Experience" required />
                      </div>
                      <div className="form-group">
                        <label className="form-label">Content</label>
                        <textarea className="form-input" rows={4} value={formData.content} onChange={e => setFormData({ ...formData, content: e.target.value })} placeholder="Share your experience..." required />
                      </div>
                      <div className="modal-footer">
                        <button type="button" className="btn btn-outline" onClick={() => setShowContributionForm(false)}>Cancel</button>
                        <button type="submit" className="btn btn-primary">Submit</button>
                      </div>
                    </form>
                  </div>
                </div>
              )}

              {myContributions.length === 0 && !showContributionForm ? (
                <div className="empty-state">
                  <Plus className="w-12 h-12" />
                  <h3>No Contributions Yet</h3>
                  <p>You haven't added any contributions. Click "Add Contribution" to share your experience.</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {myContributions.map(c => <ContributionCard key={c.id} contribution={c} isMine={true} onResubmit={handleResubmit} />)}
                </div>
              )}
            </div>
          )}

          {activeTab === 'pending-contributions' && isTeacher && (
            <div>
              {pendingContributions.length === 0 ? (
                <div className="empty-state">
                  <CheckCircle className="w-12 h-12 text-success" />
                  <h3>All Caught Up!</h3>
                  <p>There are no pending contributions to review.</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {pendingContributions.map(c => (
                    <div key={c.id} className="card" style={{ padding: '1.25rem', borderLeft: '4px solid var(--color-warning)' }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                        <div>
                          <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{c.title}</h3>
                          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
                            {c.contribution_type} • {c.company_name || 'Unknown Company'}
                          </p>
                        </div>
                        <span className="badge badge-warning">Pending Review</span>
                      </div>
                      <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '1rem', padding: '0.75rem', backgroundColor: 'var(--color-background-soft)', borderRadius: 'var(--radius-sm)' }}>
                        {c.content}
                      </p>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                          Submitted by Student ID: {c.student_id} • {formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}
                        </p>
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => setReviewForm({ show: true, contributionId: c.id, status: 'APPROVED', reason: '' })}
                        >
                          Review
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {reviewForm.show && (
                <div className="modal-overlay" onClick={() => setReviewForm({ ...reviewForm, show: false })}>
                  <div className="modal" onClick={e => e.stopPropagation()}>
                    <div className="modal-header">
                      <h3 className="modal-title">Review Contribution</h3>
                      <button className="btn-ghost" onClick={() => setReviewForm({ ...reviewForm, show: false })}><X className="w-5 h-5" /></button>
                    </div>
                    <form onSubmit={handleReviewSubmit} className="modal-content">
                      <div className="form-group">
                        <label className="form-label">Action</label>
                        <select
                          className="form-input"
                          value={reviewForm.status}
                          onChange={e => setReviewForm({ ...reviewForm, status: e.target.value })}
                        >
                          <option value="APPROVED">Approve & Publish</option>
                          <option value="REJECTED">Reject</option>
                        </select>
                      </div>

                      {reviewForm.status === 'REJECTED' && (
                        <div className="form-group">
                          <label className="form-label">Rejection Reason</label>
                          <textarea
                            className="form-input"
                            rows={3}
                            value={reviewForm.reason}
                            onChange={e => setReviewForm({ ...reviewForm, reason: e.target.value })}
                            placeholder="Explain why this contribution was rejected..."
                            required
                          />
                        </div>
                      )}

                      <div className="modal-footer">
                        <button type="button" className="btn btn-outline" onClick={() => setReviewForm({ ...reviewForm, show: false })}>Cancel</button>
                        <button type="submit" className={`btn ${reviewForm.status === 'APPROVED' ? 'btn-primary' : 'btn-danger'}`}>
                          Confirm {reviewForm.status === 'APPROVED' ? 'Approval' : 'Rejection'}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}