import React, { useEffect, useState } from 'react'
import { dashboardApi } from '../services/api'
import { format, formatDistanceToNow } from 'date-fns'
import {
  ClipboardList,
  FileText,
  Megaphone,
  Calendar,
  GraduationCap,
  Bell,
  Mail,
  Briefcase,
  AlertTriangle,
  TrendingUp,
  ExternalLink,
} from 'lucide-react'

const statusColors = {
  upcoming: 'badge-primary',
  overdue: 'badge-danger',
  completed: 'badge-success',
  unread: 'badge-primary',
  read: 'badge-secondary',
}

const statusLabels = {
  upcoming: 'Upcoming',
  overdue: 'Overdue',
  completed: 'Completed',
  unread: 'Unread',
  read: 'Read',
}

function StatCard({ title, value, icon: Icon, trend, trendUp = true, loading }) {
  if (loading) {
    return (
      <div className="card">
        <div
          className="card-content"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
          }}
        >
          <div
            className="animate-pulse"
            style={{
              width: '48px',
              height: '48px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-primary-light)',
            }}
          />

          <div style={{ flex: 1 }}>
            <div
              className="animate-pulse"
              style={{
                height: '1.5rem',
                width: '60%',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--color-border)',
              }}
            />

            <div
              className="animate-pulse"
              style={{
                height: '2.5rem',
                width: '40%',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--color-border)',
                marginTop: '0.5rem',
              }}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div
        className="card-content"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--color-primary-light)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--color-primary)',
          }}
        >
          <Icon className="w-6 h-6" />
        </div>

        <div>
          <p
            style={{
              fontSize: '0.875rem',
              color: 'var(--color-text-secondary)',
              fontWeight: 500,
            }}
          >
            {title}
          </p>

          <p
            style={{
              fontSize: '1.5rem',
              fontWeight: 700,
              color: 'var(--color-text)',
            }}
          >
            {value}
          </p>

          {trend && (
            <p
              style={{
                fontSize: '0.75rem',
                color: trendUp
                  ? 'var(--color-success)'
                  : 'var(--color-danger)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem',
                marginTop: '0.25rem',
              }}
            >
              <TrendingUp
                className={`w-4 h-4 ${!trendUp ? 'rotate-180' : ''}`}
              />
              {trend}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function AssignmentItem({ assignment }) {
  const dueDate = new Date(assignment.due_date)
  const isOverdue = assignment.status === 'overdue'

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.75rem 0',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <p
          style={{
            fontWeight: 500,
            color: 'var(--color-text)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {assignment.title}
        </p>

        <p
          style={{
            fontSize: '0.8125rem',
            color: 'var(--color-text-secondary)',
          }}
        >
          {assignment.subject_code || 'Unknown Subject'}
        </p>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          whiteSpace: 'nowrap',
        }}
      >
        <span className={`badge ${statusColors[assignment.status]}`}>
          {statusLabels[assignment.status]}
        </span>

        <time
          style={{
            fontSize: '0.8125rem',
            color: isOverdue
              ? 'var(--color-danger)'
              : 'var(--color-text-secondary)',
          }}
        >
          {format(dueDate, 'MMM d, yyyy')}
        </time>
      </div>
    </div>
  )
}

function ExamItem({ exam }) {
  const examDate = new Date(exam.exam_date)
  const daysUntil = Math.ceil(
    (examDate - new Date()) / (1000 * 60 * 60 * 24)
  )

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.75rem 0',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <p
          style={{
            fontWeight: 500,
            color: 'var(--color-text)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {exam.title}
        </p>

        <p
          style={{
            fontSize: '0.8125rem',
            color: 'var(--color-text-secondary)',
          }}
        >
          {exam.subject_code || 'Unknown Subject'} • {exam.exam_type}
        </p>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          whiteSpace: 'nowrap',
        }}
      >
        <span className="badge badge-primary">{daysUntil} days</span>

        <time
          style={{
            fontSize: '0.8125rem',
            color: 'var(--color-text-secondary)',
          }}
        >
          {format(examDate, 'MMM d, yyyy')}
        </time>
      </div>
    </div>
  )
}

function AnnouncementItem({ announcement }) {
  const pubDate = new Date(announcement.published_at)

  return (
    <div
      style={{
        padding: '0.75rem 0',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.75rem',
        }}
      >
        <span
          className="badge badge-secondary"
          style={{
            marginTop: '0.125rem',
            fontSize: '0.6875rem',
          }}
        >
          {announcement.category}
        </span>

        <div style={{ flex: 1, minWidth: 0 }}>
          <p
            style={{
              fontWeight: 500,
              color: 'var(--color-text)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {announcement.title}
          </p>

          <p
            style={{
              fontSize: '0.8125rem',
              color: 'var(--color-text-secondary)',
            }}
          >
            {announcement.source_name || 'Unknown Source'} •{' '}
            {formatDistanceToNow(pubDate, { addSuffix: true })}
          </p>
        </div>
      </div>
    </div>
  )
}

function AttendanceItem({ record }) {
  const color =
    record.attendance_percentage >= 75
      ? 'var(--color-success)'
      : record.attendance_percentage >= 60
        ? 'var(--color-warning)'
        : 'var(--color-danger)'

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.75rem 0',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <p
          style={{
            fontWeight: 500,
            color: 'var(--color-text)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {record.subject_name ||
            record.subject_code ||
            'Overall Attendance'}
        </p>

        <p
          style={{
            fontSize: '0.8125rem',
            color: 'var(--color-text-secondary)',
          }}
        >
          {record.classes_attended || 0} / {record.total_classes || 0}{' '}
          classes
        </p>
      </div>

      <div style={{ textAlign: 'right' }}>
        <p
          style={{
            fontSize: '1.125rem',
            fontWeight: 700,
            color,
          }}
        >
          {Number(record.attendance_percentage || 0).toFixed(1)}%
        </p>

        {record.is_unavailable && (
          <span
            className="badge badge-warning"
            style={{ fontSize: '0.6875rem' }}
          >
            Unavailable
          </span>
        )}
      </div>
    </div>
  )
}

function ReminderItem({ reminder }) {
  const triggerTime = new Date(reminder.trigger_time)
  const isPast =
    reminder.trigger_time < new Date().toISOString()

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.75rem 0',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <p
          style={{
            fontWeight: 500,
            color: 'var(--color-text)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {reminder.title}
        </p>

        {reminder.description && (
          <p
            style={{
              fontSize: '0.8125rem',
              color: 'var(--color-text-secondary)',
            }}
          >
            {reminder.description}
          </p>
        )}
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          whiteSpace: 'nowrap',
        }}
      >
        <span
          className={`badge ${
            reminder.status === 'processed'
              ? 'badge-success'
              : reminder.status === 'cancelled'
                ? 'badge-secondary'
                : 'badge-warning'
          }`}
        >
          {statusLabels[reminder.status] || reminder.status}
        </span>

        <time
          style={{
            fontSize: '0.8125rem',
            color:
              isPast && reminder.status === 'pending'
                ? 'var(--color-danger)'
                : 'var(--color-text-secondary)',
          }}
        >
          {format(triggerTime, 'MMM d, HH:mm')}
        </time>
      </div>
    </div>
  )
}

function PlacementItem({ opportunity }) {
  return (
    <div
      style={{
        padding: '0.75rem 0',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <p
        style={{
          fontWeight: 500,
          color: 'var(--color-text)',
        }}
      >
        {opportunity.title}
      </p>

      <p
        style={{
          fontSize: '0.8125rem',
          color: 'var(--color-text-secondary)',
        }}
      >
        {opportunity.company_name || 'Unknown Company'}
      </p>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '1rem',
          marginTop: '0.5rem',
          flexWrap: 'wrap',
        }}
      >
        {opportunity.location && (
          <span
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.25rem',
              fontSize: '0.8125rem',
              color: 'var(--color-text-secondary)',
            }}
          >
            <ExternalLink className="w-4 h-4" />
            {opportunity.location}
          </span>
        )}

        {opportunity.package_details && (
          <span className="badge badge-success">
            {opportunity.package_details}
          </span>
        )}

        {opportunity.application_deadline && (
          <time
            style={{
              fontSize: '0.8125rem',
              color: 'var(--color-text-secondary)',
            }}
          >
            Apply by{' '}
            {format(
              new Date(opportunity.application_deadline),
              'MMM d'
            )}
          </time>
        )}
      </div>
    </div>
  )
}

function SectionCard({
  title,
  icon: Icon,
  children,
  emptyMessage,
  loading,
  action,
}) {
  return (
    <div
      className="card"
      style={{
        minHeight: '280px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div className="card-header">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <Icon
            className="w-5 h-5"
            style={{ color: 'var(--color-primary)' }}
          />
          <h3 className="card-title">{title}</h3>
        </div>

        {action}
      </div>

      <div
        className="card-content"
        style={{
          flex: 1,
          overflow: 'hidden',
        }}
      >
        {loading ? (
          <div className="loading" style={{ flex: 1 }}>
            <div
              className="animate-pulse"
              style={{
                height: '100%',
                background:
                  'linear-gradient(90deg, var(--color-border) 25%, var(--color-primary-light) 50%, var(--color-border) 75%)',
                backgroundSize: '200% 100%',
                animation: 'loading 1.5s infinite',
              }}
            />
          </div>
        ) : React.Children.count(children) === 0 ? (
          <div className="empty-state" style={{ flex: 1 }}>
            <p>{emptyMessage}</p>
          </div>
        ) : (
          <div
            style={{
              overflowY: 'auto',
              maxHeight: '320px',
            }}
          >
            {children}
          </div>
        )}
      </div>
    </div>
  )
}

export function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await dashboardApi.get()
        setData(response.data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div
        className="grid grid-4"
        style={{ marginBottom: '1.5rem' }}
      >
        <StatCard
          title="Upcoming Assignments"
          value="—"
          icon={ClipboardList}
          loading
        />

        <StatCard
          title="Overdue Assignments"
          value="—"
          icon={AlertTriangle}
          loading
        />

        <StatCard
          title="Upcoming Exams"
          value="—"
          icon={FileText}
          loading
        />

        <StatCard
          title="Unread Notifications"
          value="—"
          icon={Mail}
          loading
        />
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle className="w-12 h-12" />

        <h3>Failed to load dashboard</h3>

        <p>{error}</p>
      </div>
    )
  }

  const {
    upcoming_assignments = [],
    overdue_assignments = [],
    upcoming_examinations = [],
    recent_announcements = [],
    attendance_summary = {},
    academic_summary = [],
    pending_reminders = [],
    unread_notifications_count = 0,
    placement_opportunities = [],
    unavailable_sections = [],
  } = data || {}

  const isUnavailable = (section) =>
    unavailable_sections.includes(section)

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1
          style={{
            fontSize: '1.5rem',
            fontWeight: 600,
            marginBottom: '0.25rem',
          }}
        >
          Dashboard
        </h1>

        <p
          style={{
            color: 'var(--color-text-secondary)',
          }}
        >
          Overview of your academic attention items
        </p>
      </div>

      <div
        className="grid grid-4"
        style={{ marginBottom: '1.5rem' }}
      >
        <StatCard
          title="Upcoming Assignments"
          value={
            isUnavailable('assignments')
              ? '—'
              : upcoming_assignments.length
          }
          icon={ClipboardList}
          trend={
            !isUnavailable('assignments') &&
            overdue_assignments.length > 0
              ? `${overdue_assignments.length} overdue`
              : null
          }
          trendUp={false}
          loading={false}
        />

        <StatCard
          title="Upcoming Exams"
          value={
            isUnavailable('examinations')
              ? '—'
              : upcoming_examinations.length
          }
          icon={FileText}
          trend={
            !isUnavailable('examinations') &&
            upcoming_examinations.length > 0
              ? `${Math.max(
                  0,
                  Math.ceil(
                    (new Date(
                      upcoming_examinations[0].exam_date
                    ) -
                      new Date()) /
                      (1000 * 60 * 60 * 24)
                  )
                )} days`
              : null
          }
          trendUp
          loading={false}
        />

        <StatCard
          title="Attendance"
          value={
            isUnavailable('attendance')
              ? '—'
              : `${attendance_summary.overall_percentage || 0}%`
          }
          icon={Calendar}
          trend={
            !isUnavailable('attendance')
              ? `${attendance_summary.total_classes_attended || 0}/${attendance_summary.total_classes || 0} classes`
              : null
          }
          trendUp={
            !isUnavailable('attendance') &&
            attendance_summary.overall_percentage >= 75
          }
          loading={false}
        />

        <StatCard
          title="Unread Notifications"
          value={
            isUnavailable('notifications')
              ? '—'
              : unread_notifications_count
          }
          icon={Mail}
          loading={false}
        />
      </div>

      <div
        className="grid grid-2"
        style={{ marginBottom: '1.5rem' }}
      >
        <SectionCard
          title="Upcoming Assignments"
          icon={ClipboardList}
          children={
            isUnavailable('assignments')
              ? null
              : upcoming_assignments
                  .slice(0, 5)
                  .map((assignment) => (
                    <AssignmentItem
                      key={assignment.id}
                      assignment={assignment}
                    />
                  ))
          }
          emptyMessage={
            isUnavailable('assignments')
              ? 'Assignment information is currently unavailable.'
              : 'No upcoming assignments'
          }
          loading={false}
        />

        <SectionCard
          title="Overdue Assignments"
          icon={AlertTriangle}
          children={
            isUnavailable('assignments')
              ? null
              : overdue_assignments
                  .slice(0, 5)
                  .map((assignment) => (
                    <AssignmentItem
                      key={assignment.id}
                      assignment={assignment}
                    />
                  ))
          }
          emptyMessage={
            isUnavailable('assignments')
              ? 'Assignment information is currently unavailable.'
              : 'No overdue assignments'
          }
          loading={false}
        />
      </div>

      <div
        className="grid grid-2"
        style={{ marginBottom: '1.5rem' }}
      >
        <SectionCard
          title="Upcoming Examinations"
          icon={FileText}
          children={
            isUnavailable('examinations')
              ? null
              : upcoming_examinations
                  .slice(0, 5)
                  .map((exam) => (
                    <ExamItem
                      key={exam.id}
                      exam={exam}
                    />
                  ))
          }
          emptyMessage={
            isUnavailable('examinations')
              ? 'Examination information is currently unavailable.'
              : 'No upcoming examinations'
          }
          loading={false}
        />

        <SectionCard
          title="Recent Announcements"
          icon={Megaphone}
          children={
            isUnavailable('announcements')
              ? null
              : recent_announcements
                  .slice(0, 5)
                  .map((announcement) => (
                    <AnnouncementItem
                      key={announcement.id}
                      announcement={announcement}
                    />
                  ))
          }
          emptyMessage={
            isUnavailable('announcements')
              ? 'Announcement information is currently unavailable.'
              : 'No recent announcements'
          }
          loading={false}
        />
      </div>

      <div
        className="grid grid-2"
        style={{ marginBottom: '1.5rem' }}
      >
        <SectionCard
          title="Attendance Summary"
          icon={Calendar}
          children={
            isUnavailable('attendance')
              ? null
              : Object.entries(attendance_summary).length > 0 ? (
                  <>
                    <AttendanceItem
                      record={{
                        ...attendance_summary,
                        subject_name: 'Overall Attendance',
                        attendance_percentage:
                          attendance_summary.overall_percentage || 0,
                      }}
                    />

                    {attendance_summary.records
                      ?.slice(0, 3)
                      .map((record) => (
                        <AttendanceItem
                          key={record.id}
                          record={record}
                        />
                      ))}
                  </>
                ) : null
          }
          emptyMessage={
            isUnavailable('attendance')
              ? 'Attendance information is currently unavailable.'
              : 'Attendance data unavailable. Sync from portal.'
          }
          loading={false}
        />

        <SectionCard
          title="Pending Reminders"
          icon={Bell}
          children={
            isUnavailable('reminders')
              ? null
              : pending_reminders
                  .slice(0, 5)
                  .map((reminder) => (
                    <ReminderItem
                      key={reminder.id}
                      reminder={reminder}
                    />
                  ))
          }
          emptyMessage={
            isUnavailable('reminders')
              ? 'Reminder information is currently unavailable.'
              : 'No pending reminders'
          }
          loading={false}
        />
      </div>

      <div className="grid grid-2">
        <SectionCard
          title="Academic Summary"
          icon={GraduationCap}
          children={
            isUnavailable('academics')
              ? null
              : academic_summary
                  .slice(0, 5)
                  .map((record) => (
                    <div
                      key={record.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                        padding: '0.75rem 0',
                        borderBottom:
                          '1px solid var(--color-border)',
                      }}
                    >
                      <div
                        style={{
                          flex: 1,
                          minWidth: 0,
                        }}
                      >
                        <p
                          style={{
                            fontWeight: 500,
                            color: 'var(--color-text)',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {record.subject_name ||
                            record.subject_code ||
                            'Unknown Subject'}
                        </p>

                        <p
                          style={{
                            fontSize: '0.8125rem',
                            color:
                              'var(--color-text-secondary)',
                          }}
                        >
                          Semester {record.semester}
                        </p>
                      </div>

                      <div style={{ textAlign: 'right' }}>
                        <p
                          style={{
                            fontSize: '1rem',
                            fontWeight: 600,
                            color: 'var(--color-text)',
                          }}
                        >
                          {record.grade || '—'}
                        </p>

                        <p
                          style={{
                            fontSize: '0.75rem',
                            color: 'var(--color-text-muted)',
                          }}
                        >
                          {record.total_marks || 0} /{' '}
                          {(record.max_internal_marks || 0) +
                            (record.max_external_marks || 0)}
                        </p>
                      </div>
                    </div>
                  ))
          }
          emptyMessage={
            isUnavailable('academics')
              ? 'Academic information is currently unavailable.'
              : 'No academic records available'
          }
          loading={false}
        />

        <SectionCard
          title="Placement Opportunities"
          icon={Briefcase}
          children={
            isUnavailable('placements')
              ? null
              : placement_opportunities
                  .slice(0, 3)
                  .map((opportunity) => (
                    <PlacementItem
                      key={opportunity.id}
                      opportunity={opportunity}
                    />
                  ))
          }
          emptyMessage={
            isUnavailable('placements')
              ? 'Placement information is currently unavailable.'
              : 'No open placement opportunities'
          }
          loading={false}
        />
      </div>
    </div>
  )
}