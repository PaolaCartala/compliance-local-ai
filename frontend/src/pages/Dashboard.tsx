import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  Upload,
  TrendingUp,
  Users,
  Shield
} from "lucide-react";
import { ComplianceStatus } from "@/components/ComplianceStatus";
import { FinancialMetric } from "@/components/FinancialMetric";
import { mockTodayStats, mockRecentMeetings, mockComplianceDashboard } from "@/data/mockData";

export default function Dashboard() {
  const { pending_reviews, audit_metrics, security_status } = mockComplianceDashboard;

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                SEC Compliance Dashboard
              </h1>
              <p className="text-muted-foreground mt-1">
                AI Financial Assistant for Wealth Management
              </p>
            </div>
            <div className="flex items-center gap-3">
              <ComplianceStatus status="secure" />
              <Button variant="trust" size="lg">
                <Upload className="w-4 h-4" />
                Process New Notes
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-success/20 bg-success-light/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-success flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Today's Approved
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FinancialMetric 
                label="Notes Processed"
                value={mockTodayStats.approved_notes}
                trend="up"
                change={12}
                size="lg"
              />
            </CardContent>
          </Card>

          <Card className="border-warning/20 bg-warning-light/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-warning flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Pending Review
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FinancialMetric 
                label="Items in Queue"
                value={mockTodayStats.pending_reviews}
                trend="neutral"
                size="lg"
              />
            </CardContent>
          </Card>

          <Card className="border-primary/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-primary flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                AI Confidence
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FinancialMetric 
                label="Average Score"
                value={mockTodayStats.avg_confidence}
                format="percentage"
                trend="up"
                change={3}
                size="lg"
              />
            </CardContent>
          </Card>

          <Card className="border-primary/20">
            <CardHeader className="pb-3">
              <CardTitle className="text-primary flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Compliance Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FinancialMetric 
                label="SEC Standards"
                value={mockTodayStats.compliance_rate}
                format="percentage"
                trend="neutral"
                size="lg"
              />
            </CardContent>
          </Card>
        </div>

        {/* Recent Meetings & Pending Reviews */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Meetings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Recent Meeting Notes
              </CardTitle>
              <CardDescription>
                Latest processed client meetings with AI analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {mockRecentMeetings.slice(0, 4).map((meeting) => (
                <div key={meeting.id} className="flex items-center justify-between p-3 border rounded-lg data-row-hover">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h4 className="font-medium text-sm">{meeting.client_name}</h4>
                      <ComplianceStatus 
                        status={meeting.status as any} 
                        size="sm"
                      />
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{meeting.type}</span>
                      <span>•</span>
                      <span>{meeting.date}</span>
                      <span>•</span>
                      <span>{meeting.duration}</span>
                    </div>
                  </div>
                  <div className="text-right space-y-1">
                    <Badge variant="secondary" className="font-mono text-xs">
                      {meeting.ai_confidence}% AI
                    </Badge>
                    <p className="text-xs text-muted-foreground">{meeting.advisor}</p>
                  </div>
                </div>
              ))}
              <div className="pt-2">
                <Button variant="outline" className="w-full">
                  View All Meetings
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Queue */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Compliance Review Queue
              </CardTitle>
              <CardDescription>
                Items requiring human review and approval
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {pending_reviews.map((review) => (
                <div key={review.id} className="flex items-center justify-between p-3 border rounded-lg data-row-hover">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h4 className="font-medium text-sm">{review.client_name}</h4>
                      {review.requires_attention && (
                        <Badge variant="destructive" className="text-xs">
                          High Priority
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Meeting: {review.meeting_date}</span>
                      <span>•</span>
                      <span>AI: {review.ai_confidence}%</span>
                      {review.regulatory_flags > 0 && (
                        <>
                          <span>•</span>
                          <span className="text-warning">{review.regulatory_flags} flags</span>
                        </>
                      )}
                    </div>
                  </div>
                  <Button variant="compliance" size="sm">
                    Review
                  </Button>
                </div>
              ))}
              <div className="pt-2">
                <Button variant="trust" className="w-full">
                  Open Review Queue
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Security & System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Security & System Status
            </CardTitle>
            <CardDescription>
              Real-time security monitoring and compliance verification
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-3">
                <h4 className="font-medium text-sm">Data Security</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Encryption Status</span>
                    <ComplianceStatus status="secure" size="sm">
                      {security_status.encryption_status}
                    </ComplianceStatus>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Access Violations</span>
                    <Badge variant="secondary" className="font-mono">
                      {security_status.access_violations}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Audit Trail</span>
                    <ComplianceStatus status="secure" size="sm">
                      {security_status.audit_trail_integrity}
                    </ComplianceStatus>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-medium text-sm">Processing Metrics</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Notes Today</span>
                    <Badge variant="secondary" className="font-mono">
                      {audit_metrics.notes_processed_today}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Avg Review Time</span>
                    <Badge variant="secondary" className="font-mono">
                      {audit_metrics.human_review_time_avg}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>SEC Compliance</span>
                    <ComplianceStatus status="approved" size="sm">
                      {audit_metrics.sec_compliance_rate}
                    </ComplianceStatus>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="font-medium text-sm">Integration Status</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Redtail CRM</span>
                    <ComplianceStatus status="secure" size="sm">
                      Connected
                    </ComplianceStatus>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Albridge Portfolio</span>
                    <ComplianceStatus status="secure" size="sm">
                      Active
                    </ComplianceStatus>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span>Black Diamond</span>
                    <ComplianceStatus status="pending" size="sm">
                      Planning
                    </ComplianceStatus>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}