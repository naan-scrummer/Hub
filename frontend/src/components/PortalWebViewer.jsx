import React, { useState } from 'react'
import { Globe, RefreshCw, ExternalLink, X, ArrowRight, Home } from 'lucide-react'

export function PortalWebViewer({ defaultUrl = 'https://example.com', onClose }) {
  const [urlInput, setUrlInput] = useState(defaultUrl)
  const [activeUrl, setActiveUrl] = useState(defaultUrl)
  const [iframeKey, setIframeKey] = useState(0)

  const handleNavigate = (e) => {
    if (e) e.preventDefault()
    let url = urlInput.trim()
    if (!url) return
    if (!/^https?:\/\//i.test(url)) {
      url = 'https://' + url
    }
    setActiveUrl(url)
    setUrlInput(url)
    setIframeKey(k => k + 1)
  }

  const handleResetPortal = () => {
    setUrlInput(defaultUrl)
    setActiveUrl(defaultUrl)
    setIframeKey(k => k + 1)
  }

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 220px)', minHeight: '600px', boxShadow: 'var(--shadow-md)', border: '1px solid var(--color-border)' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0.625rem 1rem',
        background: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        gap: '0.75rem',
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1, minWidth: '280px', maxWidth: '720px' }}>
          <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexShrink: 0 }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#ef4444', display: 'inline-block' }} />
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#f59e0b', display: 'inline-block' }} />
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }} />
          </div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={handleResetPortal}
            title="Reset to default portal URL"
            style={{ padding: '0.25rem 0.5rem', display: 'flex', alignItems: 'center', color: 'var(--color-text-secondary)', flexShrink: 0 }}
          >
            <Home className="w-4 h-4" />
          </button>
          <form onSubmit={handleNavigate} style={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0, margin: 0 }}>
            <div style={{
              position: 'relative',
              display: 'flex',
              alignItems: 'center',
              width: '100%',
              background: 'var(--color-background)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.25rem 0.6rem',
              gap: '0.5rem'
            }}>
              <Globe className="w-4 h-4" style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
              <input
                type="text"
                value={urlInput}
                onChange={e => setUrlInput(e.target.value)}
                placeholder="Enter website URL (e.g. https://...)"
                style={{
                  border: 'none',
                  outline: 'none',
                  background: 'transparent',
                  width: '100%',
                  fontSize: '0.8125rem',
                  color: 'var(--color-text)'
                }}
              />
              <button
                type="submit"
                className="btn btn-ghost btn-sm"
                title="Go to URL"
                style={{ padding: '0.125rem 0.35rem', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', flexShrink: 0 }}
              >
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setIframeKey(k => k + 1)}
            title="Reload website"
            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
          >
            <RefreshCw className="w-4 h-4" />
            <span>Reload</span>
          </button>
          <a
            href={activeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline btn-sm"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
            title="Open in new tab"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Open in Tab</span>
          </a>
          {onClose && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={onClose}
              title="Close website view"
              style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--color-danger)' }}
            >
              <X className="w-4 h-4" />
              <span>Close</span>
            </button>
          )}
        </div>
      </div>

      <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%', minHeight: '520px', background: '#ffffff' }}>
        <iframe
          key={iframeKey}
          src={activeUrl}
          title="Portal Web View"
          style={{
            width: '100%',
            height: '100%',
            minHeight: '520px',
            border: 'none',
            display: 'block'
          }}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  )
}
