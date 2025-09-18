import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  File, 
  FileText,
  Download,
  Clock,
  CheckCircle,
  Upload,
  Users,
  TrendingUp,
  Shield,
  Plus
} from 'lucide-react';
import { ComplianceStatus } from '@/components/ComplianceStatus';
import { TemplateCompletionModal } from '@/components/TemplateCompletionModal';

export default function FillTemplates() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<{name: string; category: string} | null>(null);
  const templateCategories = [
    {
      id: 'meeting_notes',
      name: 'Meeting Notes',
      icon: Users,
      color: 'blue',
      templates: [
        { name: 'Quarterly Review Template', status: 'active', uses: 142 },
        { name: 'Annual Planning Template', status: 'active', uses: 89 },
        { name: 'Initial Client Meeting', status: 'active', uses: 56 },
        { name: 'Risk Assessment Review', status: 'draft', uses: 12 }
      ]
    },
    {
      id: 'investment_docs',
      name: 'Investment Documentation',
      icon: TrendingUp,
      color: 'green',
      templates: [
        { name: 'Investment Policy Statement', status: 'active', uses: 78 },
        { name: 'Portfolio Rebalancing Report', status: 'active', uses: 134 },
        { name: 'Risk Tolerance Questionnaire', status: 'active', uses: 67 },
        { name: 'Investment Recommendation Form', status: 'review', uses: 23 }
      ]
    },
    {
      id: 'compliance_forms',
      name: 'Compliance Forms',
      icon: Shield,
      color: 'red',
      templates: [
        { name: 'SEC Compliance Checklist', status: 'active', uses: 89 },
        { name: 'Client Suitability Assessment', status: 'active', uses: 156 },
        { name: 'Trade Authorization Form', status: 'active', uses: 234 },
        { name: 'Regulatory Filing Template', status: 'active', uses: 45 }
      ]
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'review': return 'warning';
      case 'draft': return 'secondary';
      default: return 'secondary';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Active';
      case 'review': return 'In Review';
      case 'draft': return 'Draft';
      default: return 'Unknown';
    }
  };

  const handleFillTemplate = (templateName: string, categoryName: string) => {
    setSelectedTemplate({ name: templateName, category: categoryName });
    setModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Fill Templates
              </h1>
              <p className="text-muted-foreground mt-1">
                Pre-built SEC-compliant document templates for efficient workflow
              </p>
            </div>
            <div className="flex items-center gap-3">
              <ComplianceStatus status="secure" />
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Create Template
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <File className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-bold">16</p>
                  <p className="text-sm text-muted-foreground">Active Templates</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-success" />
                </div>
                <div>
                  <p className="text-2xl font-bold">1,247</p>
                  <p className="text-sm text-muted-foreground">Documents Created</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-warning" />
                </div>
                <div>
                  <p className="text-2xl font-bold">4</p>
                  <p className="text-sm text-muted-foreground">Pending Review</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-neutral/10 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-neutral" />
                </div>
                <div>
                  <p className="text-2xl font-bold">100%</p>
                  <p className="text-sm text-muted-foreground">SEC Compliant</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Template Categories */}
        <div className="space-y-8">
          {templateCategories.map((category) => {
            const Icon = category.icon;
            return (
              <Card key={category.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg bg-${category.color}-100 flex items-center justify-center`}>
                        <Icon className={`w-5 h-5 text-${category.color}-600`} />
                      </div>
                      <div>
                        <CardTitle>{category.name}</CardTitle>
                        <CardDescription>
                          {category.templates.length} templates available
                        </CardDescription>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Template
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {category.templates.map((template, index) => (
                      <Card key={index} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <FileText className="w-4 h-4 text-muted-foreground" />
                                <h4 className="font-medium text-sm">{template.name}</h4>
                              </div>
                              <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3">
                                <Badge 
                                  variant={getStatusColor(template.status) as any}
                                  className="text-xs"
                                >
                                  {getStatusText(template.status)}
                                </Badge>
                                <span>{template.uses} uses</span>
                              </div>
                              <div className="flex gap-2">
                                <Button 
                                  size="sm" 
                                  variant="outline" 
                                  className="h-8 text-xs"
                                  onClick={() => handleFillTemplate(template.name, category.name)}
                                >
                                  <Upload className="w-3 h-3 mr-1" />
                                  Fill
                                </Button>
                                <Button size="sm" variant="ghost" className="h-8 text-xs">
                                  <Download className="w-3 h-3 mr-1" />
                                  Download
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Template Activity</CardTitle>
            <CardDescription>
              Latest document creation and template usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { template: 'Quarterly Review Template', client: 'Robert J. Smith', time: '2 hours ago', status: 'completed' },
                { template: 'Investment Policy Statement', client: 'Maria Gonzalez', time: '4 hours ago', status: 'completed' },
                { template: 'SEC Compliance Checklist', client: 'System Review', time: '6 hours ago', status: 'completed' },
                { template: 'Risk Assessment Review', client: 'James Chen', time: '1 day ago', status: 'pending' },
              ].map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg data-row-hover">
                  <div className="space-y-1">
                    <h4 className="font-medium text-sm">{activity.template}</h4>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Client: {activity.client}</span>
                      <span>•</span>
                      <span>{activity.time}</span>
                    </div>
                  </div>
                  <ComplianceStatus 
                    status={activity.status === 'completed' ? 'approved' : 'pending'} 
                    size="sm"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Template Completion Modal */}
        <TemplateCompletionModal 
          open={modalOpen}
          onOpenChange={setModalOpen}
          template={selectedTemplate}
        />
      </div>
    </div>
  );
}