import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ComplianceStatus } from "@/components/ComplianceStatus";
import { mockMeetingNoteResult, mockComplianceDashboard } from "@/data/mockData";
import { 
  Shield, 
  Clock, 
  User, 
  FileText, 
  Download,
  Search,
  Filter,
  Eye,
  Lock,
  CheckCircle,
  AlertTriangle,
  Calendar,
  Database
} from "lucide-react";

interface AuditEvent {
  id: string;
  timestamp: string;
  event_type: string;
  user: string;
  client_name?: string;
  action: string;
  details: string;
  ip_address?: string;
  status: "success" | "warning" | "error";
  retention_date: string;
}

const mockAuditEvents: AuditEvent[] = [
  {
    id: "audit_001",
    timestamp: "2025-09-10T16:45:00Z",
    event_type: "note_approval",
    user: "Jennifer Walsh, CCO",
    client_name: "Robert J. Smith",
    action: "Approved meeting notes",
    details: "Quarterly review notes approved and posted to Redtail CRM",
    ip_address: "192.168.1.45",
    status: "success",
    retention_date: "2031-09-10"
  },
  {
    id: "audit_002", 
    timestamp: "2025-09-10T16:30:00Z",
    event_type: "ai_processing",
    user: "System AI",
    client_name: "Robert J. Smith",
    action: "AI note generation",
    details: "Meeting transcript processed with 96% confidence score",
    status: "success",
    retention_date: "2031-09-10"
  },
  {
    id: "audit_003",
    timestamp: "2025-09-10T14:30:00Z",
    event_type: "file_upload",
    user: "Sarah Johnson, CFP",
    client_name: "Robert J. Smith",
    action: "Audio file uploaded",
    details: "Meeting recording uploaded (47m 23s duration)",
    ip_address: "192.168.1.23",
    status: "success",
    retention_date: "2031-09-10"
  },
  {
    id: "audit_004",
    timestamp: "2025-09-10T11:15:00Z",
    event_type: "security_scan",
    user: "System Security",
    action: "Security scan completed",
    details: "Daily security scan - no vulnerabilities detected",
    status: "success",
    retention_date: "2026-09-10"
  },
  {
    id: "audit_005",
    timestamp: "2025-09-09T16:45:00Z",
    event_type: "compliance_flag",
    user: "Jennifer Walsh, CCO",
    client_name: "Maria Gonzalez",
    action: "Flagged for review",
    details: "Complex investment recommendation requires additional documentation",
    ip_address: "192.168.1.45",
    status: "warning",
    retention_date: "2031-09-09"
  },
  {
    id: "audit_006",
    timestamp: "2025-09-09T14:20:00Z",
    event_type: "crm_integration",
    user: "System Integration",
    client_name: "James Chen", 
    action: "CRM data sync",
    details: "Client profile synchronized with Redtail CRM",
    status: "success",
    retention_date: "2031-09-09"
  }
];

export default function AuditTrail() {
  const [searchTerm, setSearchTerm] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const filteredEvents = mockAuditEvents.filter((event) => {
    const matchesSearch = event.client_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.details.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = eventTypeFilter === "all" || event.event_type === eventTypeFilter;
    const matchesStatus = statusFilter === "all" || event.status === statusFilter;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="w-4 h-4 text-success" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case "error":
        return <AlertTriangle className="w-4 h-4 text-destructive" />;
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />;
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case "note_approval":
        return <CheckCircle className="w-4 h-4 text-success" />;
      case "ai_processing":
        return <Database className="w-4 h-4 text-primary" />;
      case "file_upload":
        return <FileText className="w-4 h-4 text-blue-500" />;
      case "security_scan":
        return <Shield className="w-4 h-4 text-primary" />;
      case "compliance_flag":
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case "crm_integration":
        return <User className="w-4 h-4 text-green-500" />;
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />;
    }
  };

  const formatEventType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audit Trail</h1>
          <p className="text-muted-foreground">
            Complete immutable record of all system activities for regulatory compliance
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <ComplianceStatus status="secure" />
          <Button className="gap-2">
            <Download className="w-4 h-4" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-primary/10 rounded-lg">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <div>
                <div className="text-2xl font-bold">142</div>
                <div className="text-sm text-muted-foreground">Events Today</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-success/10 rounded-lg">
                <CheckCircle className="w-6 h-6 text-success" />
              </div>
              <div>
                <div className="text-2xl font-bold">100%</div>
                <div className="text-sm text-muted-foreground">Compliance Rate</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-warning/10 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-warning" />
              </div>
              <div>
                <div className="text-2xl font-bold">3</div>
                <div className="text-sm text-muted-foreground">Flags This Week</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center p-6">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Lock className="w-6 h-6 text-primary" />
              </div>
              <div>
                <div className="text-2xl font-bold">6 Years</div>
                <div className="text-sm text-muted-foreground">Retention Period</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input 
                placeholder="Search events, users, or clients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          <Select value={eventTypeFilter} onValueChange={setEventTypeFilter}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Event Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Event Types</SelectItem>
              <SelectItem value="note_approval">Note Approval</SelectItem>
              <SelectItem value="ai_processing">AI Processing</SelectItem>
              <SelectItem value="file_upload">File Upload</SelectItem>
              <SelectItem value="security_scan">Security Scan</SelectItem>
              <SelectItem value="compliance_flag">Compliance Flag</SelectItem>
              <SelectItem value="crm_integration">CRM Integration</SelectItem>
            </SelectContent>
          </Select>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="success">Success</SelectItem>
              <SelectItem value="warning">Warning</SelectItem>
              <SelectItem value="error">Error</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Audit Events */}
      <Tabs defaultValue="events" className="space-y-4">
        <TabsList>
          <TabsTrigger value="events" className="gap-2">
            <Eye className="w-4 h-4" />
            Audit Events ({filteredEvents.length})
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2">
            <Shield className="w-4 h-4" />
            Security Log
          </TabsTrigger>
          <TabsTrigger value="compliance" className="gap-2">
            <CheckCircle className="w-4 h-4" />
            Compliance Reports
          </TabsTrigger>
        </TabsList>

        <TabsContent value="events" className="space-y-4">
          {filteredEvents.map((event) => (
            <Card key={event.id} className="border-l-4 border-l-primary/20">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="p-2 bg-muted rounded-lg">
                      {getEventIcon(event.event_type)}
                    </div>
                    
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">{event.action}</h4>
                        <Badge variant="secondary">{formatEventType(event.event_type)}</Badge>
                        {getStatusIcon(event.status)}
                      </div>
                      
                      <p className="text-sm text-muted-foreground">{event.details}</p>
                      
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <User className="w-3 h-3" />
                          {event.user}
                        </span>
                        {event.client_name && (
                          <span>Client: {event.client_name}</span>
                        )}
                        {event.ip_address && (
                          <span>IP: {event.ip_address}</span>
                        )}
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          Retain until: {new Date(event.retention_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      {new Date(event.timestamp).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Security Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h4 className="font-medium">Encryption Status</h4>
                  <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg">
                    <span>AES-256 Encryption</span>
                    <ComplianceStatus status="approved" showIcon={false}>Active</ComplianceStatus>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Access Control</h4>
                  <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg">
                    <span>Role-Based Access</span>
                    <ComplianceStatus status="approved" showIcon={false}>Enabled</ComplianceStatus>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Audit Trail Integrity</h4>
                  <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg">
                    <span>Tamper Detection</span>
                    <ComplianceStatus status="approved" showIcon={false}>Verified</ComplianceStatus>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Data Retention</h4>
                  <div className="flex items-center justify-between p-3 bg-success/10 rounded-lg">
                    <span>SEC Compliance</span>
                    <ComplianceStatus status="approved" showIcon={false}>Current</ComplianceStatus>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance">
          <Card>
            <CardContent className="flex items-center justify-center py-12">
              <div className="text-center space-y-3">
                <CheckCircle className="w-12 h-12 text-success mx-auto" />
                <h3 className="text-lg font-medium">100% SEC Compliance Rate</h3>
                <p className="text-muted-foreground">All regulatory requirements met for the current period</p>
                <Button className="mt-4">Generate Compliance Report</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}