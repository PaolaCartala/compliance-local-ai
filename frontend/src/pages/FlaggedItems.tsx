import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ComplianceStatus } from "@/components/ComplianceStatus";
import { mockFlaggedItems } from "@/data/mockData";
import { 
  Flag,
  AlertTriangle, 
  Clock, 
  Eye, 
  CheckCircle,
  XCircle,
  User,
  Calendar,
  TrendingUp,
  ArrowUp,
  ArrowLeft,
  MessageSquare
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Link } from "react-router-dom";

export default function FlaggedItems() {
  const [selectedFilter, setSelectedFilter] = useState<string>("all");
  const { toast } = useToast();
  
  const handleResolve = (itemId: string, clientName: string) => {
    toast({
      title: "Item Resolved",
      description: `${clientName} flagged item has been resolved and approved.`,
    });
  };

  const handleEscalate = (itemId: string, clientName: string) => {
    toast({
      title: "Item Escalated",
      description: `${clientName} flagged item has been escalated to supervisor.`,
      variant: "destructive",
    });
  };

  const getPriorityBadge = (priority: string) => {
    return priority === "high" ? (
      <Badge variant="destructive" className="gap-1">
        <AlertTriangle className="w-3 h-3" />
        High Priority
      </Badge>
    ) : (
      <Badge variant="secondary" className="gap-1">
        <Clock className="w-3 h-3" />
        Normal
      </Badge>
    );
  };

  const getResolutionStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge variant="secondary" className="gap-1"><Clock className="w-3 h-3" />Pending</Badge>;
      case "in_progress":
        return <Badge variant="outline" className="gap-1"><TrendingUp className="w-3 h-3" />In Progress</Badge>;
      case "resolved":
        return <Badge variant="default" className="gap-1"><CheckCircle className="w-3 h-3" />Resolved</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getEscalationBadge = (level: string) => {
    switch (level) {
      case "supervisor":
        return <Badge variant="outline" className="gap-1"><ArrowUp className="w-3 h-3" />Supervisor</Badge>;
      case "compliance_officer":
        return <Badge variant="destructive" className="gap-1"><ArrowUp className="w-3 h-3" />Compliance Officer</Badge>;
      default:
        return <Badge variant="secondary">{level}</Badge>;
    }
  };

  const filteredItems = mockFlaggedItems.filter(item => {
    if (selectedFilter === "all") return true;
    return item.resolution_status === selectedFilter;
  });

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Link to="/review">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Review Queue
          </Button>
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Flagged Items</h1>
          <p className="text-muted-foreground">
            Review and resolve items requiring additional compliance attention
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm font-medium">
              {filteredItems.length} Flagged Items
            </div>
            <div className="text-xs text-muted-foreground">
              Avg Resolution Time: 2.5 days
            </div>
          </div>
          <ComplianceStatus status="flagged" />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <Select value={selectedFilter} onValueChange={setSelectedFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Items</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-4">
        {filteredItems.map((item) => (
          <Card key={item.id} className="border-l-4 border-l-destructive">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <User className="w-5 h-5" />
                    {item.client_name}
                  </CardTitle>
                  <CardDescription className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      Meeting: {new Date(item.meeting_date).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1">
                      <Flag className="w-4 h-4" />
                      Flagged: {new Date(item.flagged_date).toLocaleDateString()}
                    </span>
                  </CardDescription>
                </div>
                
                <div className="flex items-center gap-2">
                  {getPriorityBadge(item.priority)}
                  {getResolutionStatusBadge(item.resolution_status)}
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="flex items-start gap-3 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                <Flag className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <p className="font-medium text-destructive">{item.flag_category}</p>
                    {getEscalationBadge(item.escalation_level)}
                  </div>
                  <p className="text-sm text-muted-foreground">{item.flag_reason}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Flagged by: {item.flagged_by} • Est. Resolution: {item.estimated_resolution_time}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium">Flag Details</h4>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div>Category: {item.flag_category}</div>
                    <div>AI Confidence: {item.ai_confidence}%</div>
                    <div>Escalation Level: {item.escalation_level.replace('_', ' ')}</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Resolution Timeline</h4>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div>Status: {item.resolution_status.replace('_', ' ')}</div>
                    <div>Est. Time: {item.estimated_resolution_time}</div>
                    <div>Created: {new Date(item.created).toLocaleDateString()}</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Review Information</h4>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div>Flagged By: {item.flagged_by}</div>
                    <div>Meeting Type: Quarterly Review</div>
                    <div>Priority: {item.priority}</div>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <Button variant="outline" className="gap-2">
                  <Eye className="w-4 h-4" />
                  View Details
                </Button>

                <div className="flex items-center gap-2">
                  <Button 
                    variant="outline" 
                    className="gap-2"
                    onClick={() => handleEscalate(item.id, item.client_name)}
                  >
                    <ArrowUp className="w-4 h-4" />
                    Escalate
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    className="gap-2"
                  >
                    <MessageSquare className="w-4 h-4" />
                    Add Note
                  </Button>
                  
                  <Button 
                    className="gap-2"
                    onClick={() => handleResolve(item.id, item.client_name)}
                  >
                    <CheckCircle className="w-4 h-4" />
                    Resolve & Approve
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredItems.length === 0 && (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center space-y-3">
              <CheckCircle className="w-12 h-12 text-success mx-auto" />
              <h3 className="text-lg font-medium">No Flagged Items</h3>
              <p className="text-muted-foreground">
                {selectedFilter === "all" 
                  ? "All items are currently in compliance" 
                  : `No items with status: ${selectedFilter}`}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}