import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { 
  User, 
  DollarSign, 
  TrendingUp, 
  Shield, 
  Calendar,
  FileText,
  CheckCircle,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';
import { mockClients, mockPortfolios } from '@/data/mockData';

interface TemplateCompletionModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  template: {
    name: string;
    category: string;
  } | null;
}

type Step = 'template' | 'client' | 'portfolio' | 'details' | 'compliance';

export function TemplateCompletionModal({ open, onOpenChange, template }: TemplateCompletionModalProps) {
  const [currentStep, setCurrentStep] = useState<Step>('template');
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [selectedPortfolio, setSelectedPortfolio] = useState<string>('');
  const [meetingDate, setMeetingDate] = useState('');
  const [meetingType, setMeetingType] = useState('');
  const [objectives, setObjectives] = useState('');

  const steps: { key: Step; title: string; description: string }[] = [
    { key: 'template', title: 'Template Details', description: 'Confirm template selection' },
    { key: 'client', title: 'Select Client', description: 'Choose client from CRM' },
    { key: 'portfolio', title: 'Portfolio Review', description: 'Review portfolio data' },
    { key: 'details', title: 'Meeting Details', description: 'Enter meeting information' },
    { key: 'compliance', title: 'Compliance Check', description: 'Verify and complete' }
  ];

  const currentStepIndex = steps.findIndex(step => step.key === currentStep);
  const progressPercent = ((currentStepIndex + 1) / steps.length) * 100;

  const handleNext = () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStep(steps[currentStepIndex + 1].key);
    }
  };

  const handleBack = () => {
    if (currentStepIndex > 0) {
      setCurrentStep(steps[currentStepIndex - 1].key);
    }
  };

  const selectedClientData = mockClients.find(client => client.id === selectedClient);
  const selectedPortfolioData = mockPortfolios.find(portfolio => portfolio.client_id === selectedClient);

  const canProceed = () => {
    switch (currentStep) {
      case 'template': return true;
      case 'client': return selectedClient !== '';
      case 'portfolio': return selectedPortfolio !== '';
      case 'details': return meetingDate && meetingType;
      case 'compliance': return true;
      default: return false;
    }
  };

  const handleComplete = () => {
    // Here would be the actual completion logic
    console.log('Template completion:', {
      template,
      selectedClient,
      selectedPortfolio,
      meetingDate,
      meetingType,
      objectives
    });
    onOpenChange(false);
    // Reset form
    setCurrentStep('template');
    setSelectedClient('');
    setSelectedPortfolio('');
    setMeetingDate('');
    setMeetingType('');
    setObjectives('');
  };

  if (!template) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-primary" />
            Complete Template: {template.name}
          </DialogTitle>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Step {currentStepIndex + 1} of {steps.length}</span>
            <span>{Math.round(progressPercent)}% Complete</span>
          </div>
          <Progress value={progressPercent} className="w-full" />
          <p className="text-sm text-muted-foreground">
            {steps[currentStepIndex].description}
          </p>
        </div>

        <Separator />

        {/* Step Content */}
        <div className="space-y-6">
          {currentStep === 'template' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-success" />
                  Template Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Template Name</Label>
                    <p className="font-medium">{template.name}</p>
                  </div>
                  <div>
                    <Label>Category</Label>
                    <Badge variant="secondary">{template.category}</Badge>
                  </div>
                </div>
                <div>
                  <Label>Description</Label>
                  <p className="text-sm text-muted-foreground">
                    SEC-compliant template for standardized documentation and regulatory compliance.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {currentStep === 'client' && (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="w-5 h-5 text-primary" />
                    Select Client
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="client-select">Client</Label>
                      <Select value={selectedClient} onValueChange={setSelectedClient}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose a client from CRM" />
                        </SelectTrigger>
                        <SelectContent>
                          {mockClients.map((client) => (
                            <SelectItem key={client.id} value={client.id}>
                              <div className="flex items-center justify-between w-full">
                                <span>{client.name}</span>
                                <span className="text-xs text-muted-foreground ml-2">
                                  {client.account_number}
                                </span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {selectedClientData && (
                      <Card className="bg-muted/50">
                        <CardContent className="p-4">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <Label>Risk Tolerance</Label>
                              <p>{selectedClientData.risk_tolerance}</p>
                            </div>
                            <div>
                              <Label>Investment Objective</Label>
                              <p>{selectedClientData.investment_objective}</p>
                            </div>
                            <div>
                              <Label>Primary Advisor</Label>
                              <p>{selectedClientData.primary_advisor}</p>
                            </div>
                            <div>
                              <Label>Relationship Type</Label>
                              <p>{selectedClientData.relationship_type}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentStep === 'portfolio' && selectedPortfolioData && (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-success" />
                    Portfolio Overview
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <DollarSign className="w-8 h-8 mx-auto mb-2 text-primary" />
                      <p className="text-2xl font-bold">
                        ${selectedPortfolioData.total_portfolio_value.toLocaleString()}
                      </p>
                      <p className="text-sm text-muted-foreground">Total Value</p>
                    </div>
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <TrendingUp className="w-8 h-8 mx-auto mb-2 text-success" />
                      <p className="text-2xl font-bold">
                        +{selectedPortfolioData.performance_summary['Year-to-Date']}%
                      </p>
                      <p className="text-sm text-muted-foreground">YTD Performance</p>
                    </div>
                    <div className="text-center p-4 bg-muted/50 rounded-lg">
                      <Shield className="w-8 h-8 mx-auto mb-2 text-neutral" />
                      <p className="text-2xl font-bold">{selectedClientData?.risk_tolerance}</p>
                      <p className="text-sm text-muted-foreground">Risk Profile</p>
                    </div>
                  </div>

                  <div>
                    <Label>Asset Allocation</Label>
                    <div className="grid grid-cols-2 gap-2 text-sm mt-2">
                      {Object.entries(selectedPortfolioData.asset_allocation).map(([asset, percentage]) => (
                        <div key={asset} className="flex justify-between">
                          <span>{asset}</span>
                          <span className="font-medium">{percentage}%</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="portfolio-select">Portfolio Account</Label>
                    <Select value={selectedPortfolio} onValueChange={setSelectedPortfolio}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select portfolio account" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={selectedPortfolioData.albridge_account}>
                          {selectedPortfolioData.albridge_account} - Primary Account
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentStep === 'details' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-primary" />
                  Meeting Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="meeting-date">Meeting Date</Label>
                    <Input
                      id="meeting-date"
                      type="date"
                      value={meetingDate}
                      onChange={(e) => setMeetingDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="meeting-type">Meeting Type</Label>
                    <Select value={meetingType} onValueChange={setMeetingType}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select meeting type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="quarterly">Quarterly Review</SelectItem>
                        <SelectItem value="annual">Annual Planning</SelectItem>
                        <SelectItem value="initial">Initial Consultation</SelectItem>
                        <SelectItem value="ad-hoc">Ad-hoc Meeting</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="objectives">Meeting Objectives (Optional)</Label>
                  <Textarea
                    id="objectives"
                    placeholder="Enter meeting objectives and agenda items..."
                    value={objectives}
                    onChange={(e) => setObjectives(e.target.value)}
                    rows={4}
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {currentStep === 'compliance' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-success" />
                  Compliance Verification
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-4">
                  <div className="flex items-center justify-between p-4 bg-success/10 border border-success/20 rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-success" />
                      <span>SEC Compliance Requirements</span>
                    </div>
                    <Badge variant="secondary">Verified</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-success/10 border border-success/20 rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-success" />
                      <span>Client Data Validation</span>
                    </div>
                    <Badge variant="secondary">Verified</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-success/10 border border-success/20 rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-success" />
                      <span>Template Completion Check</span>
                    </div>
                    <Badge variant="secondary">Complete</Badge>
                  </div>
                </div>

                <div className="bg-muted/50 p-4 rounded-lg">
                  <h4 className="font-medium mb-2">Summary</h4>
                  <div className="text-sm space-y-1">
                    <p><strong>Template:</strong> {template.name}</p>
                    <p><strong>Client:</strong> {selectedClientData?.name}</p>
                    <p><strong>Meeting Date:</strong> {meetingDate}</p>
                    <p><strong>Meeting Type:</strong> {meetingType}</p>
                    {objectives && <p><strong>Objectives:</strong> {objectives}</p>}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Footer Actions */}
        <Separator />
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStepIndex === 0}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            {currentStepIndex < steps.length - 1 ? (
              <Button onClick={handleNext} disabled={!canProceed()}>
                Next
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button onClick={handleComplete} disabled={!canProceed()}>
                <CheckCircle className="w-4 h-4 mr-2" />
                Complete Template
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}