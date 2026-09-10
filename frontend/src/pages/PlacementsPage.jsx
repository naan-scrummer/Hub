import React, { useEffect, useState } from 'react'
import { placementsApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import { Briefcase, RefreshCw, AlertTriangle, Loader2, Plus, ExternalLink, Building, MapPin, DollarSign, Calendar } from 'lucide-react'

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

function ContributionCard({ contribution }) {
  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
        <div>
          <h3 style={{ fontWeight: 600, color: 'var(--color-text)' }}>{contribution.title}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginTop: '0.25rem' }}>
            {contribution.contribution_type} • {contribution.company_name || 'Unknown Company'}
          </p>
        </div>
        <span className={`badge ${contribution.is_published ? 'badge-success' : 'badge-secondary'}`}>
          {contribution.is_published ? 'Published' : 'Draft'}
        </span>
      </div>
      <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>{contribution.content}</p>
      <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
        {formatDistanceToNow(new Date(contribution.created_at), { addSuffix: true })}
      </p>
    </div>
  )
}

export function PlacementsPage() {
  const [opportunities, setOpportunities] = useState([])
  const [contributions, setContributions] = useState([])
  const [myContributions, setMyContributions] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [activeTab, setActiveTab] = useState('opportunities')
  const [showContributionForm, setShowContributionForm] = useState(false)
  const [error, setError] = useState(null)

  const [formData, setFormData] = useState({
    company_id: '',
    title: '',
    content: '',
    contribution_type: 'interview_experience',
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [oppRes, contribRes, myContribRes] = await Promise.all([
          placementsApi.getOpportunities(),
          placementsApi.getContributions(),
          placementsApi.getMyContributions(),
        ])
        setOpportunities(oppRes.data.opportunities || [])
        setContributions(contribRes.data.contributions || [])
        setMyContributions(myContribRes.data.contributions || [])
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
      await placementsApi.sync()
      const oppRes = await placementsApi.getOpportunities()
      setOpportunities(oppRes.data.opportunities || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  const handleSubmitContribution = async (e) => {
    e.preventDefault()
    try {
      await placementsApi.createContribution(formData)
      setShowContributionForm(false)
      setFormData({ company_id: '', title: '', content: '', contribution_type: 'interview_experience' })
      const myContribRes = await placementsApi.getMyContributions()
      setMyContributions(myContribRes.data.contributions || [])
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
    { id: 'my-contributions', label: 'My Contributions', count: myContributions.length, icon: Plus },
  ]

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>Placements</h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>Career opportunities and peer contributions</p>
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
                    <select className="form-input" value={formData.company_id} onChange={e => setFormData({...formData, company_id: e.target.value})} required>
                      <option value="">Select company</option>
                      {[
                        {id: '1', name: 'TechCorp Solutions'},
                        {id: '2', name: 'DataFlow Analytics'},
                        {id: '3', name: 'CloudNine Systems'},
                      ].map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Type</label>
                    <select className="form-input" value={formData.contribution_type} onChange={e => setFormData({...formData, contribution_type: e.target.value})} required>
                      <option value="interview_experience">Interview Experience</option>
                      <option value="preparation_resource">Preparation Resource</option>
                      <option value="tips">Tips & Advice</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Title</label>
                    <input className="form-input" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} placeholder="e.g., My TechCorp Interview Experience" required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Content</label>
                    <textarea className="form-input" rows={4} value={formData.content} onChange={e => setFormData({...formData, content: e.target.value})} placeholder="Share your experience..." required />
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
              {myContributions.map(c => <ContributionCard key={c.id} contribution={c} />)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}