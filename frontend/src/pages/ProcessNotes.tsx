import { useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Upload, Mic, FileText, CheckCircle, Clock, AlertTriangle, User, Calendar, Shield } from "lucide-react";
import { ComplianceStatus } from "@/components/ComplianceStatus";
import { mockMeetingNoteResult, mockCRMIntegration } from "@/data/mockData";
export default function ProcessNotes() {
  const [uploadMethod, setUploadMethod] = useState<"audio" | "text">("text");
  const [processingState, setProcessingState] = useState<"idle" | "processing" | "complete">("idle");
  const [selectedClient, setSelectedClient] = useState("");
  const [meetingType, setMeetingType] = useState("");
  const [meetingNotes, setMeetingNotes] = useState("Meeting with Robert Smith on September 10, 2025. Discussed retirement planning goals and increased 401k contributions. Client mentioned daughter starting college next year. Reviewed current portfolio performance and discussed rebalancing strategy...");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      setMeetingNotes(text);
    } catch (error) {
      console.error("Error reading file:", error);
    }
  };
  const handleProcess = () => {
    setProcessingState("processing");
    // Simulate AI processing
    setTimeout(() => {
      setProcessingState("complete");
    }, 3000);
  };
  const clientOptions = [{
    value: "RT_12345",
    label: "Robert J. Smith (RTS-789456123)"
  }, {
    value: "RT_12346",
    label: "Maria Gonzalez (MG-456789123)"
  }, {
    value: "RT_12347",
    label: "James Chen (JC-123456789)"
  }, {
    value: "RT_12348",
    label: "Lisa Rodriguez (LR-987654321)"
  }];
  const meetingTypes = ["Quarterly Review", "Annual Review", "Investment Review", "Risk Assessment", "Financial Planning Session", "Portfolio Rebalancing", "Tax Planning Meeting"];
  return <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Process Meeting Notes
              </h1>
              <p className="text-muted-foreground mt-1">
                Upload audio recordings or text to generate SEC-compliant documentation
              </p>
            </div>
            <ComplianceStatus status="secure" />
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Meeting Information
                </CardTitle>
                <CardDescription>
                  Provide client details and meeting context for accurate processing
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Client Selection */}
                <div className="space-y-2">
                  <Label htmlFor="client">Client (Redtail CRM Integration)</Label>
                  <Select value={selectedClient} onValueChange={setSelectedClient}>
                    <SelectTrigger>
                      <SelectValue placeholder="Search and select client..." />
                    </SelectTrigger>
                    <SelectContent>
                      {clientOptions.map(client => <SelectItem key={client.value} value={client.value}>
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4" />
                            {client.label}
                          </div>
                        </SelectItem>)}
                    </SelectContent>
                  </Select>
                  {selectedClient === "RT_12345" && <div className="p-3 bg-success-light/30 border border-success/20 rounded-lg text-sm">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-4 h-4 text-success" />
                        <span className="font-medium">Client Profile Loaded</span>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        <div>
                          <p className="text-muted-foreground">AUM</p>
                          <p className="font-medium">{mockCRMIntegration.client_profile.assets_under_management}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Risk Tolerance</p>
                          <p className="font-medium">{mockCRMIntegration.client_profile.risk_tolerance}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Advisor</p>
                          <p className="font-medium">{mockCRMIntegration.client_profile.primary_advisor}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Last Review</p>
                          <p className="font-medium">{mockCRMIntegration.client_profile.last_annual_review}</p>
                        </div>
                      </div>
                    </div>}
                </div>

                {/* Meeting Type */}
                <div className="space-y-2">
                  <Label htmlFor="meeting-type">Meeting Type</Label>
                  <Select value={meetingType} onValueChange={setMeetingType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select meeting type..." />
                    </SelectTrigger>
                    <SelectContent>
                      {meetingTypes.map(type => <SelectItem key={type} value={type}>
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            {type}
                          </div>
                        </SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>

                {/* Meeting Date */}
                <div className="space-y-2">
                  <Label htmlFor="meeting-date">Meeting Date</Label>
                  <Input type="date" defaultValue="2025-09-10" className="font-mono" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {uploadMethod === "audio" ? <Mic className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                  Upload Method
                </CardTitle>
                <CardDescription>
                  Choose your preferred input method for meeting notes
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Method Selection */}
                <div className="flex gap-2">
                  <Button variant="outline" disabled className="flex-1 opacity-50 cursor-not-allowed">
                    <Mic className="w-4 h-4" />
                    Audio Recording (Coming Soon)
                  </Button>
                  <Button variant={uploadMethod === "text" ? "trust" : "outline"} onClick={() => setUploadMethod("text")} className="flex-1">
                    <FileText className="w-4 h-4" />
                    Text Input
                  </Button>
                </div>

                {uploadMethod === "audio" ? <div className="space-y-4">
                    <div className="border-2 border-dashed border-muted-foreground/20 rounded-lg p-8 text-center">
                      <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="font-medium mb-2">Drop audio file here</h3>
                      <p className="text-sm text-muted-foreground mb-4">
                        Supports M4A, WAV, MP3 files from iPhone or other devices
                      </p>
                      <Button variant="outline">
                        Select Audio File
                      </Button>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Shield className="w-4 h-4" />
                      <span>Audio files are processed securely and deleted after transcription</span>
                    </div>
                  </div> : <div className="space-y-4">
                    <Textarea placeholder="Paste your meeting transcript or notes here..." className="min-h-32 font-mono text-sm" value={meetingNotes} onChange={e => setMeetingNotes(e.target.value)} />
                    
                    {/* File Upload Button */}
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()}>
                        <Upload className="w-4 h-4" />
                        Upload File
                      </Button>
                      <span className="text-sm text-muted-foreground">Upload .txt, .doc, .docx, .md, .rtf files</span>
                      <input ref={fileInputRef} type="file" accept=".txt,.doc,.docx,.rtf,.md" onChange={handleFileUpload} className="hidden" />
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Shield className="w-4 h-4" />
                      <span>Text is processed securely with end-to-end encryption</span>
                    </div>
                  </div>}

                <Button variant="trust" size="lg" className="w-full" onClick={handleProcess} disabled={processingState === "processing" || !selectedClient || !meetingType}>
                  {processingState === "processing" ? <>
                      <Clock className="w-4 h-4 animate-spin" />
                      Processing with AI...
                    </> : <>
                      <Shield className="w-4 h-4" />
                      Generate SEC-Compliant Notes
                    </>}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Results Display */}
          <div className="space-y-6">
            {processingState === "idle" && <Card className="border-dashed">
                <CardContent className="flex items-center justify-center py-12">
                  <div className="text-center text-muted-foreground">
                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>SEC-compliant notes will appear here after processing</p>
                  </div>
                </CardContent>
              </Card>}

            {processingState === "processing" && <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 animate-spin text-primary" />
                    Processing Meeting Notes
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-4 h-4 text-success" />
                      <span className="text-sm">Audio transcribed successfully</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Clock className="w-4 h-4 text-primary animate-spin" />
                      <span className="text-sm">Generating SEC-compliant format...</span>
                    </div>
                    <div className="flex items-center gap-3 opacity-50">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">Flagging for compliance review</span>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-muted/30 rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      AI Confidence: <span className="font-mono font-bold text-primary">96%</span>
                    </p>
                  </div>
                </CardContent>
              </Card>}

            {processingState === "complete" && <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-success" />
                    SEC-Compliant Meeting Notes Generated
                  </CardTitle>
                  <CardDescription>
                    AI processing complete - Review required before approval
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Client Information Header */}
                  <div className="p-4 bg-card-subtle rounded-lg border">
                    <h3 className="font-semibold mb-2">Client Information</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Client Name</p>
                        <p className="font-medium">{mockMeetingNoteResult.client_information.name}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Account Number</p>
                        <p className="font-mono">{mockMeetingNoteResult.client_information.account_number}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Meeting Type</p>
                        <p className="font-medium">{mockMeetingNoteResult.client_information.meeting_type}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Advisor</p>
                        <p className="font-medium">{mockMeetingNoteResult.client_information.advisor}</p>
                      </div>
                    </div>
                  </div>

                  {/* Discussion Topics */}
                  <div className="space-y-4">
                    <h3 className="font-semibold">Discussion Topics</h3>
                    {mockMeetingNoteResult.discussion_topics.slice(0, 2).map((topic, index) => <div key={index} className="p-4 border rounded-lg">
                        <h4 className="font-medium text-primary mb-2">{topic.category}</h4>
                        <p className="text-sm mb-3">{topic.content}</p>
                        <div className="flex items-center gap-2 text-xs">
                          <Shield className="w-3 h-3 text-success" />
                          <span className="text-muted-foreground">{topic.regulatory_notes}</span>
                        </div>
                      </div>)}
                  </div>

                  {/* Recommendations */}
                  <div className="space-y-3">
                    <h3 className="font-semibold">Recommendations Given</h3>
                    <div className="p-4 border rounded-lg">
                      <p className="font-medium text-sm mb-2">{mockMeetingNoteResult.recommendations_given[0].recommendation}</p>
                      <p className="text-sm text-muted-foreground mb-2">{mockMeetingNoteResult.recommendations_given[0].rationale}</p>
                      <div className="flex items-center gap-2 text-xs">
                        <CheckCircle className="w-3 h-3 text-success" />
                        <span className="text-success">Fiduciary standard applied</span>
                      </div>
                    </div>
                  </div>

                  {/* Compliance Status */}
                  <div className="p-4 bg-success-light/20 border border-success/20 rounded-lg">
                    <div className="flex items-center gap-2 mb-3">
                      <Shield className="w-4 h-4 text-success" />
                      <h3 className="font-semibold text-success">Compliance Verification</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-3 h-3 text-success" />
                        <span>SEC Requirements Met</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-3 h-3 text-success" />
                        <span>Fiduciary Standard Applied</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-3 h-3 text-success" />
                        <span>Suitability Documented</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-3 h-3 text-success" />
                        <span>No Conflicts of Interest</span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <Button variant="trust" className="flex-1">
                      Send for Review
                    </Button>
                    <Button variant="outline" className="flex-1">
                      Edit Notes
                    </Button>
                  </div>

                  {/* Processing Info */}
                  <div className="p-3 bg-muted/30 rounded-lg text-sm space-y-2">
                    <div className="flex justify-between">
                      <span>AI Confidence Score:</span>
                      <span className="font-mono font-bold text-primary">96%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Processing Time:</span>
                      <span className="font-mono">2m 15s</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <ComplianceStatus status="pending" size="sm">
                        Awaiting Review
                      </ComplianceStatus>
                    </div>
                  </div>
                </CardContent>
              </Card>}
          </div>
        </div>
      </div>
    </div>;
}