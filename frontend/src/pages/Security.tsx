import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ComplianceStatus } from "@/components/ComplianceStatus";
import { mockSecurityData } from "@/data/mockData";
import { 
  Shield,
  Lock,
  Eye,
  AlertTriangle,
  CheckCircle,
  Users,
  Activity,
  Clock,
  Globe,
  Database,
  FileText,
  Zap
} from "lucide-react";

export default function Security() {
  const { security_metrics, recent_security_events, compliance_monitoring, access_control } = mockSecurityData;

  const getRiskLevelBadge = (level: string) => {
    switch (level) {
      case "low":
        return <Badge variant="default" className="gap-1"><CheckCircle className="w-3 h-3" />Low Risk</Badge>;
      case "medium":
        return <Badge variant="secondary" className="gap-1"><AlertTriangle className="w-3 h-3" />Medium Risk</Badge>;
      case "high":
        return <Badge variant="destructive" className="gap-1"><AlertTriangle className="w-3 h-3" />High Risk</Badge>;
      default:
        return <Badge variant="outline">{level}</Badge>;
    }
  };

  const getComplianceStatus = (status: string) => {
    return status === "compliant" ? (
      <div className="flex items-center gap-1 text-success">
        <CheckCircle className="w-4 h-4" />
        <span className="text-sm font-medium">Compliant</span>
      </div>
    ) : (
      <div className="flex items-center gap-1 text-destructive">
        <AlertTriangle className="w-4 h-4" />
        <span className="text-sm font-medium">Non-Compliant</span>
      </div>
    );
  };

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case "login_success":
        return <CheckCircle className="w-4 h-4 text-success" />;
      case "failed_login":
        return <AlertTriangle className="w-4 h-4 text-destructive" />;
      case "data_access":
        return <Eye className="w-4 h-4 text-primary" />;
      default:
        return <Activity className="w-4 h-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor system security, access control, and compliance status
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm font-medium">
              Last Security Scan
            </div>
            <div className="text-xs text-muted-foreground">
              {new Date(security_metrics.last_security_scan).toLocaleString()}
            </div>
          </div>
          <ComplianceStatus status="secure" />
        </div>
      </div>

      {/* Security Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-success/10 rounded-lg">
                <Shield className="w-5 h-5 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium">Encryption Status</p>
                <p className="text-lg font-bold text-success">{security_metrics.encryption_status}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Users className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium">Active Sessions</p>
                <p className="text-lg font-bold">{security_metrics.active_sessions}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-warning/10 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-warning" />
              </div>
              <div>
                <p className="text-sm font-medium">Failed Logins (24h)</p>
                <p className="text-lg font-bold text-warning">{security_metrics.failed_login_attempts}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-success/10 rounded-lg">
                <CheckCircle className="w-5 h-5 text-success" />
              </div>
              <div>
                <p className="text-sm font-medium">Vulnerabilities</p>
                <p className="text-lg font-bold text-success">{security_metrics.vulnerability_count}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Access Control */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lock className="w-5 h-5" />
              Access Control
            </CardTitle>
            <CardDescription>User access and authentication monitoring</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Total Users</span>
                  <span className="font-medium">{access_control.total_users}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Sessions</span>
                  <span className="font-medium">{access_control.active_sessions}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Failed Attempts</span>
                  <span className="font-medium text-warning">{access_control.failed_access_attempts}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">2FA Status</span>
                  <Badge variant="default">Enforced</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Role-Based Access</span>
                  <Badge variant="default">Enabled</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Privileged Reviews</span>
                  <span className="font-medium">{access_control.privileged_access_reviews}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Compliance Monitoring */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Compliance Status
            </CardTitle>
            <CardDescription>SEC and regulatory compliance monitoring</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">SEC Requirements</span>
              {getComplianceStatus(compliance_monitoring.sec_requirements_status)}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Data Encryption</span>
              {getComplianceStatus(compliance_monitoring.data_encryption_compliance)}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Record Retention</span>
              {getComplianceStatus(compliance_monitoring.record_retention_compliance)}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Access Control</span>
              {getComplianceStatus(compliance_monitoring.access_control_compliance)}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Audit Trail</span>
              {getComplianceStatus(compliance_monitoring.audit_trail_compliance)}
            </div>
            <Separator />
            <div className="text-xs text-muted-foreground">
              Last Check: {new Date(compliance_monitoring.last_compliance_check).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Security Events */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Recent Security Events
          </CardTitle>
          <CardDescription>Latest security activities and access logs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recent_security_events.map((event) => (
              <div key={event.id} className="flex items-start gap-3 p-3 bg-muted/30 rounded-lg">
                <div className="flex-shrink-0 mt-0.5">
                  {getEventTypeIcon(event.event_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-sm">
                      {event.event_type.replace('_', ' ').toUpperCase()}
                    </span>
                    {getRiskLevelBadge(event.risk_level)}
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{event.details}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3" />
                      {event.user}
                    </span>
                    <span className="flex items-center gap-1">
                      <Globe className="w-3 h-3" />
                      {event.ip_address}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(event.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            System Security Status
          </CardTitle>
          <CardDescription>Current system security and integrity status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-success/10 rounded-lg">
              <Zap className="w-8 h-8 text-success mx-auto mb-2" />
              <p className="font-medium text-success">Data Integrity</p>
              <p className="text-sm text-muted-foreground">{security_metrics.audit_trail_integrity}</p>
            </div>
            <div className="text-center p-4 bg-success/10 rounded-lg">
              <Lock className="w-8 h-8 text-success mx-auto mb-2" />
              <p className="font-medium text-success">Encryption</p>
              <p className="text-sm text-muted-foreground">AES-256 Active</p>
            </div>
            <div className="text-center p-4 bg-success/10 rounded-lg">
              <FileText className="w-8 h-8 text-success mx-auto mb-2" />
              <p className="font-medium text-success">Retention</p>
              <p className="text-sm text-muted-foreground">{security_metrics.data_retention_compliance}</p>
            </div>
            <div className="text-center p-4 bg-success/10 rounded-lg">
              <Shield className="w-8 h-8 text-success mx-auto mb-2" />
              <p className="font-medium text-success">Access Violations</p>
              <p className="text-sm text-muted-foreground">{security_metrics.access_violations_today} Today</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}