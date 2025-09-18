import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  TrendingUp, 
  Database, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  ExternalLink,
  Cable,
  Shield,
  Zap,
  FileText,
  Search,
  Brain
} from 'lucide-react';
import { ComplianceStatus } from '@/components/ComplianceStatus';

export default function UpcomingFeatures() {
  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                Upcoming Features
              </h1>
              <p className="text-muted-foreground mt-1">
                Next-generation integrations and capabilities coming soon
              </p>
            </div>
            <div className="flex items-center gap-3">
              <ComplianceStatus status="pending" />
              <Badge variant="secondary" className="font-mono">
                <Clock className="w-3 h-3 mr-1" />
                Under Development
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Construction Notice */}
        <Card className="border-warning/20 bg-warning-light/10">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-warning-light flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-warning" />
              </div>
              <div>
                <CardTitle className="text-warning">Advanced Features In Development</CardTitle>
                <CardDescription>
                  We're building comprehensive MCP (Model Context Protocol) integrations for seamless workflow automation and enhanced AI capabilities.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-card border">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-primary" />
                    <span className="font-medium">Estimated Timeline</span>
                  </div>
                  <p className="text-sm text-muted-foreground">Q1 2026 - Full Feature Launch</p>
                </div>
                
                
                <div className="p-4 rounded-lg bg-card border">
                  <div className="flex items-center gap-2 mb-2">
                    <img src="/lovable-uploads/5cfbb876-140b-4ac9-bc63-84e5fd416aa6.png" className="w-4 h-4" alt="Baker Group Logo" />
                    <span className="font-medium">SEC Compliance</span>
                  </div>
                  <p className="text-sm text-muted-foreground">All features fully compliant</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Core Integrations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Redtail CRM Integration */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Users className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle>Redtail CRM Integration</CardTitle>
                    <CardDescription>Client relationship management and data synchronization</CardDescription>
                  </div>
                </div>
                <Badge variant="secondary">
                  <Cable className="w-3 h-3 mr-1" />
                  MCP Ready
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <h4 className="font-medium text-sm">Planned Features:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Real-time client profile synchronization
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Automated meeting note integration
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Activity logging and follow-up scheduling
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    SEC-compliant communication tracking
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Advanced workflow automation
                  </li>
                </ul>
              </div>
              
              <div className="pt-4 border-t">
                <Button variant="outline" className="w-full" disabled>
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Connect to Redtail (Coming Soon)
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Albridge Portfolio Integration */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-success" />
                  </div>
                  <div>
                    <CardTitle>Albridge Portfolio Integration</CardTitle>
                    <CardDescription>Portfolio analysis and performance monitoring</CardDescription>
                  </div>
                </div>
                <Badge variant="secondary">
                  <Cable className="w-3 h-3 mr-1" />
                  MCP Ready
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <h4 className="font-medium text-sm">Planned Features:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Live portfolio data and performance metrics
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    AI-powered investment analysis
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Risk assessment and rebalancing recommendations
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Tax-loss harvesting opportunities
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Custom reporting and alerts
                  </li>
                </ul>
              </div>
              
              <div className="pt-4 border-t">
                <Button variant="outline" className="w-full" disabled>
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Connect to Albridge (Coming Soon)
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* File Server Integration */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle>File Server Integration</CardTitle>
                    <CardDescription>Centralized document management and secure file access</CardDescription>
                  </div>
                </div>
                <Badge variant="outline">
                  <Clock className="w-3 h-3 mr-1" />
                  Future Phase
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <h4 className="font-medium text-sm">Planned Features:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Secure client document storage and retrieval
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Automated document classification and tagging
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Version control and audit trails
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Integration with meeting notes and templates
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Advanced file analytics and insights
                  </li>
                </ul>
              </div>
              
              <div className="pt-4 border-t">
                <Button variant="outline" className="w-full" disabled>
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Connect File Server (Coming Soon)
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* AI Index Integration */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                    <Brain className="w-5 h-5 text-success" />
                  </div>
                  <div>
                    <CardTitle>AI Index Integration</CardTitle>
                    <CardDescription>Intelligent knowledge base and semantic search</CardDescription>
                  </div>
                </div>
                <Badge variant="outline">
                  <Clock className="w-3 h-3 mr-1" />
                  Future Phase
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <h4 className="font-medium text-sm">Planned Features:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Semantic search across all client data
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    AI-powered content recommendations
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Intelligent document summarization
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Contextual insights and suggestions
                  </li>
                  <li className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-warning" />
                    Advanced query and analysis capabilities
                  </li>
                </ul>
              </div>
              
              <div className="pt-4 border-t">
                <Button variant="outline" className="w-full" disabled>
                  <Search className="w-4 h-4 mr-2" />
                  Connect AI Index (Coming Soon)
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Black Diamond Future Integration */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-neutral/10 flex items-center justify-center">
                  <Database className="w-5 h-5 text-neutral" />
                </div>
                <div>
                  <CardTitle>Black Diamond Integration</CardTitle>
                  <CardDescription>Advanced portfolio management and reporting platform</CardDescription>
                </div>
              </div>
              <Badge variant="outline">
                <Clock className="w-3 h-3 mr-1" />
                Future Phase
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-medium text-sm">Advanced Capabilities:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-warning" />
                    Comprehensive portfolio management
                  </li>
                  <li className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-warning" />
                    Advanced performance attribution
                  </li>
                  <li className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-warning" />
                    Multi-custodial account aggregation
                  </li>
                  <li className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-warning" />
                    Institutional-grade reporting
                  </li>
                </ul>
              </div>
              
              <div className="p-4 rounded-lg bg-accent/30 border-2 border-dashed border-accent">
                <div className="text-center space-y-2">
                  <Zap className="w-8 h-8 mx-auto text-primary" />
                  <h4 className="font-medium">Coming in 2026</h4>
                  <p className="text-sm text-muted-foreground">
                    Enhanced integration capabilities planned for the next phase of development.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* MCP Technology Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cable className="w-5 h-5" />
              Model Context Protocol (MCP) Technology
            </CardTitle>
            <CardDescription>
              Secure, compliant, and seamless integration framework
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto">
                  <img src="/lovable-uploads/5cfbb876-140b-4ac9-bc63-84e5fd416aa6.png" className="w-6 h-6" alt="Baker Group Logo" />
                </div>
                <h4 className="font-medium">SEC Compliant</h4>
                <p className="text-sm text-muted-foreground">
                  All integrations maintain strict regulatory compliance with complete audit trails.
                </p>
              </div>
              
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-lg bg-success/10 flex items-center justify-center mx-auto">
                  <Zap className="w-6 h-6 text-success" />
                </div>
                <h4 className="font-medium">Real-Time</h4>
                <p className="text-sm text-muted-foreground">
                  Live data synchronization for up-to-date client and portfolio information.
                </p>
              </div>
              
              <div className="text-center space-y-2">
                <div className="w-12 h-12 rounded-lg bg-warning/10 flex items-center justify-center mx-auto">
                  <Cable className="w-6 h-6 text-warning" />
                </div>
                <h4 className="font-medium">Seamless</h4>
                <p className="text-sm text-muted-foreground">
                  Unified experience across all platforms with intelligent context sharing.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}