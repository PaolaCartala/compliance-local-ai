import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ComplianceStatus } from "@/components/ComplianceStatus";
import { mockComplianceDashboard, mockMeetingNoteResult } from "@/data/mockData";
import { 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Eye, 
  Edit, 
  Flag,
  User,
  Calendar,
  TrendingUp,
  Shield,
  ArrowLeft
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Link } from "react-router-dom";

export default function PendingReviews() {
  const [selectedReview, setSelectedReview] = useState<string | null>(null);
  const { toast } = useToast();
  
  const handleApprove = (reviewId: string, clientName: string) => {
    toast({
      title: "Review Approved",
      description: `${clientName} meeting notes have been approved and posted to CRM.`,
    });
  };

  const handleFlag = (reviewId: string, clientName: string) => {
    toast({
      title: "Review Flagged", 
      description: `${clientName} meeting notes have been flagged for additional review.`,
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

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "text-success";
    if (confidence >= 80) return "text-warning";
    return "text-destructive";
  };

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
          <h1 className="text-3xl font-bold tracking-tight">Pending Reviews</h1>
          <p className="text-muted-foreground">
            Review and approve AI-generated meeting notes awaiting compliance verification
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm font-medium">
              {mockComplianceDashboard.pending_reviews.length} Items Pending
            </div>
            <div className="text-xs text-muted-foreground">
              Avg Review Time: {mockComplianceDashboard.audit_metrics.human_review_time_avg}
            </div>
          </div>
          <ComplianceStatus status="pending" />
        </div>
      </div>

      <div className="space-y-4">
        {mockComplianceDashboard.pending_reviews.map((review) => (
          <Card key={review.id} className="border-l-4 border-l-warning">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <User className="w-5 h-5" />
                    {review.client_name}
                  </CardTitle>
                  <CardDescription className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {new Date(review.meeting_date).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      AI Confidence: <span className={getConfidenceColor(review.ai_confidence)}>{review.ai_confidence}%</span>
                    </span>
                  </CardDescription>
                </div>
                
                <div className="flex items-center gap-2">
                  {getPriorityBadge(review.priority)}
                  {review.regulatory_flags > 0 && (
                    <Badge variant="destructive">
                      {review.regulatory_flags} Flag{review.regulatory_flags !== 1 ? 's' : ''}
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {review.requires_attention && (
                <div className="flex items-start gap-3 p-3 bg-warning/10 border border-warning/20 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-warning">Requires Attention</p>
                    <p className="text-sm text-muted-foreground">{review.flag_reason}</p>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Compliance Verification
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex items-center justify-between">
                      <span>SEC Requirements</span>
                      <CheckCircle className="w-4 h-4 text-success" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Fiduciary Standard</span>
                      <CheckCircle className="w-4 h-4 text-success" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Suitability Review</span>
                      <CheckCircle className="w-4 h-4 text-success" />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Meeting Details</h4>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div>Type: Quarterly Review</div>
                    <div>Duration: 47m 23s</div>
                    <div>Advisor: Sarah Johnson, CFP</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Processing Info</h4>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <div>Created: {new Date(review.created).toLocaleString()}</div>
                    <div>Processing Time: 2m 15s</div>
                    <div>Retention: 6 years</div>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <Button 
                  variant="outline" 
                  className="gap-2"
                  onClick={() => setSelectedReview(review.id)}
                >
                  <Eye className="w-4 h-4" />
                  View Details
                </Button>

                <div className="flex items-center gap-2">
                  <Button 
                    variant="outline" 
                    className="gap-2"
                    onClick={() => handleFlag(review.id, review.client_name)}
                  >
                    <Flag className="w-4 h-4" />
                    Flag
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    className="gap-2"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </Button>
                  
                  <Button 
                    className="gap-2"
                    onClick={() => handleApprove(review.id, review.client_name)}
                  >
                    <CheckCircle className="w-4 h-4" />
                    Approve & Post to CRM
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Review Modal */}
      {selectedReview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Detailed Review - {mockMeetingNoteResult.client_information.name}</CardTitle>
                <Button 
                  variant="ghost" 
                  onClick={() => setSelectedReview(null)}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h3 className="font-medium mb-2">Discussion Topics</h3>
                  {mockMeetingNoteResult.discussion_topics.map((topic, index) => (
                    <div key={index} className="mb-3 p-3 bg-muted/50 rounded-lg">
                      <h4 className="font-medium text-sm">{topic.category}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{topic.content}</p>
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="font-medium mb-2">Recommendations</h3>
                  {mockMeetingNoteResult.recommendations_given.map((rec, index) => (
                    <div key={index} className="mb-3 p-3 bg-muted/50 rounded-lg">
                      <h4 className="font-medium text-sm">{rec.recommendation}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{rec.rationale}</p>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}