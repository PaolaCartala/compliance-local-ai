import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Users, TrendingUp, Shield, Brain, Calculator, PiggyBank } from 'lucide-react';
import { CustomGPT, SystemPromptTemplate } from '@/types/chat';
import { mockSystemPromptTemplates } from '@/data/mockChatData';
import { useToast } from '@/hooks/use-toast';

interface CustomGPTModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  customGPT?: CustomGPT;
  mode: 'create' | 'edit';
  onSave: (customGPT: CustomGPT) => void;
}

const specializationConfig = {
  crm: { icon: Users, label: 'CRM Assistant', color: 'blue' },
  portfolio: { icon: TrendingUp, label: 'Portfolio Analyzer', color: 'green' },
  compliance: { icon: Shield, label: 'Compliance Monitor', color: 'red' },
  general: { icon: Brain, label: 'General Advisor', color: 'purple' },
  retirement: { icon: PiggyBank, label: 'Retirement Planner', color: 'indigo' },
  tax: { icon: Calculator, label: 'Tax Strategist', color: 'orange' }
};

export function CustomGPTModal({ open, onOpenChange, customGPT, mode, onSave }: CustomGPTModalProps) {
  const { toast } = useToast();
  const [formData, setFormData] = useState<Partial<CustomGPT>>({
    name: customGPT?.name || '',
    description: customGPT?.description || '',
    systemPrompt: customGPT?.systemPrompt || '',
    specialization: customGPT?.specialization || 'general',
    color: customGPT?.color || 'purple',
    icon: customGPT?.icon || 'Brain',
    mcpToolsEnabled: customGPT?.mcpToolsEnabled || {
      redtailCRM: false,
      albridgePortfolio: false,
      blackDiamond: false
    },
    isActive: customGPT?.isActive ?? true
  });

  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  const handleTemplateSelect = (templateId: string) => {
    const template = mockSystemPromptTemplates.find(t => t.id === templateId);
    if (template) {
      const config = specializationConfig[template.specialization];
      setFormData(prev => ({
        ...prev,
        name: template.name,
        description: template.description,
        systemPrompt: template.prompt,
        specialization: template.specialization,
        color: config.color,
        icon: config.icon.name,
        mcpToolsEnabled: {
          redtailCRM: template.mcpToolsRecommended.redtailCRM,
          albridgePortfolio: template.mcpToolsRecommended.albridgePortfolio,
          blackDiamond: template.mcpToolsRecommended.blackDiamond
        }
      }));
      setSelectedTemplate(templateId);
    }
  };

  const handleSpecializationChange = (specialization: CustomGPT['specialization']) => {
    const config = specializationConfig[specialization];
    setFormData(prev => ({
      ...prev,
      specialization,
      color: config.color,
      icon: config.icon.name
    }));
  };

  const handleSave = () => {
    if (!formData.name || !formData.systemPrompt) {
      toast({
        title: "Validation Error",
        description: "Name and system prompt are required fields.",
        variant: "destructive"
      });
      return;
    }

    const savedGPT: CustomGPT = {
      id: customGPT?.id || `gpt_${Date.now()}`,
      name: formData.name!,
      description: formData.description!,
      systemPrompt: formData.systemPrompt!,
      specialization: formData.specialization!,
      color: formData.color!,
      icon: formData.icon!,
      mcpToolsEnabled: formData.mcpToolsEnabled!,
      isActive: formData.isActive!,
      createdAt: customGPT?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    onSave(savedGPT);
    toast({
      title: mode === 'create' ? "CustomGPT Created" : "CustomGPT Updated",
      description: `${formData.name} has been ${mode === 'create' ? 'created' : 'updated'} successfully.`
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === 'create' ? 'Create New CustomGPT' : 'Edit CustomGPT'}
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="basic" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="basic">Basic Settings</TabsTrigger>
            <TabsTrigger value="prompt">System Prompt</TabsTrigger>
            <TabsTrigger value="integrations">MCP Integrations</TabsTrigger>
          </TabsList>

          <TabsContent value="basic" className="space-y-6">
            {mode === 'create' && (
              <Card>
                <CardHeader>
                  <CardTitle>Quick Start Templates</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {mockSystemPromptTemplates.map((template) => {
                      const config = specializationConfig[template.specialization];
                      const Icon = config.icon;
                      return (
                        <Card 
                          key={template.id}
                          className={`cursor-pointer transition-colors hover:bg-accent/50 ${
                            selectedTemplate === template.id ? 'ring-2 ring-primary' : ''
                          }`}
                          onClick={() => handleTemplateSelect(template.id)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-center gap-3 mb-2">
                              <Icon className="w-5 h-5 text-primary" />
                              <h4 className="font-medium">{template.name}</h4>
                            </div>
                            <p className="text-sm text-muted-foreground">{template.description}</p>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="e.g., Portfolio Analyzer"
                  />
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Brief description of this CustomGPT's purpose..."
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="specialization">Specialization</Label>
                  <Select
                    value={formData.specialization}
                    onValueChange={handleSpecializationChange}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(specializationConfig).map(([key, config]) => {
                        const Icon = config.icon;
                        return (
                          <SelectItem key={key} value={key}>
                            <div className="flex items-center gap-2">
                              <Icon className="w-4 h-4" />
                              {config.label}
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <div className="p-4 border rounded-lg bg-card-subtle">
                  <h4 className="font-medium mb-3">Preview</h4>
                  <div className="flex items-center gap-3 mb-3">
                    {formData.specialization && (
                      <Badge 
                        className={`bg-${formData.color}-100 text-${formData.color}-700 border-${formData.color}-200`}
                      >
                        {specializationConfig[formData.specialization]?.label}
                      </Badge>
                    )}
                  </div>
                  <h5 className="font-medium">{formData.name || 'Untitled CustomGPT'}</h5>
                  <p className="text-sm text-muted-foreground mt-1">
                    {formData.description || 'No description provided'}
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="isActive">Active Status</Label>
                  <Switch
                    id="isActive"
                    checked={formData.isActive}
                    onCheckedChange={(checked) => setFormData(prev => ({ ...prev, isActive: checked }))}
                  />
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="prompt" className="space-y-4">
            <div>
              <Label htmlFor="systemPrompt">System Prompt</Label>
              <Textarea
                id="systemPrompt"
                value={formData.systemPrompt}
                onChange={(e) => setFormData(prev => ({ ...prev, systemPrompt: e.target.value }))}
                placeholder="Enter the system prompt that defines this CustomGPT's behavior and expertise..."
                rows={12}
                className="font-mono text-sm"
              />
              <p className="text-sm text-muted-foreground mt-2">
                Define how this CustomGPT should behave, its expertise area, and any specific guidelines for SEC compliance.
              </p>
            </div>
          </TabsContent>

          <TabsContent value="integrations" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>MCP Tool Integrations</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Enable external tool access for enhanced capabilities
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Redtail CRM</h4>
                    <p className="text-sm text-muted-foreground">Access client profiles and relationship data</p>
                  </div>
                  <Switch
                    checked={formData.mcpToolsEnabled?.redtailCRM}
                    onCheckedChange={(checked) => 
                      setFormData(prev => ({
                        ...prev,
                        mcpToolsEnabled: { ...prev.mcpToolsEnabled!, redtailCRM: checked }
                      }))
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Albridge Portfolio</h4>
                    <p className="text-sm text-muted-foreground">Analyze portfolio data and performance</p>
                  </div>
                  <Switch
                    checked={formData.mcpToolsEnabled?.albridgePortfolio}
                    onCheckedChange={(checked) => 
                      setFormData(prev => ({
                        ...prev,
                        mcpToolsEnabled: { ...prev.mcpToolsEnabled!, albridgePortfolio: checked }
                      }))
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Black Diamond</h4>
                    <p className="text-sm text-muted-foreground">Advanced portfolio management (Coming Soon)</p>
                  </div>
                  <Switch
                    checked={formData.mcpToolsEnabled?.blackDiamond}
                    onCheckedChange={(checked) => 
                      setFormData(prev => ({
                        ...prev,
                        mcpToolsEnabled: { ...prev.mcpToolsEnabled!, blackDiamond: checked }
                      }))
                    }
                    disabled
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} className="bg-primary hover:bg-primary/90">
            {mode === 'create' ? 'Create CustomGPT' : 'Save Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}