// Mock data for the SEC-compliant wealth management AI system

// Mock clients data for template completion
export const mockClients = [
  {
    id: "client_001",
    name: "Robert J. Smith",
    account_number: "RTS-789456123",
    redtail_id: "RT_12345",
    date_of_birth: "1975-03-15",
    account_opening_date: "2018-06-12",
    primary_advisor: "Sarah Johnson, CFP",
    relationship_type: "Individual Advisory",
    assets_under_management: "$847,392.18",
    last_annual_review: "2024-09-15",
    next_scheduled_review: "2025-09-15",
    risk_tolerance: "Moderate",
    investment_objective: "Long-term Growth"
  },
  {
    id: "client_002", 
    name: "Maria Gonzalez",
    account_number: "MGZ-234567890",
    redtail_id: "RT_23456",
    date_of_birth: "1982-07-22",
    account_opening_date: "2020-03-10",
    primary_advisor: "Michael Chen, CFP",
    relationship_type: "Joint Advisory",
    assets_under_management: "$1,234,567.89",
    last_annual_review: "2024-08-20",
    next_scheduled_review: "2025-08-20",
    risk_tolerance: "Aggressive",
    investment_objective: "Capital Appreciation"
  },
  {
    id: "client_003",
    name: "James Chen",
    account_number: "JCH-345678901",
    redtail_id: "RT_34567",
    date_of_birth: "1968-11-15",
    account_opening_date: "2015-09-05",
    primary_advisor: "Sarah Johnson, CFP",
    relationship_type: "Individual Advisory",
    assets_under_management: "$2,856,402.34",
    last_annual_review: "2024-07-10",
    next_scheduled_review: "2025-07-10",
    risk_tolerance: "Conservative",
    investment_objective: "Capital Preservation"
  },
  {
    id: "client_004",
    name: "Emily Davis",
    account_number: "EDV-456789012",
    redtail_id: "RT_45678",
    date_of_birth: "1990-04-08",
    account_opening_date: "2022-01-15",
    primary_advisor: "Lisa Wang, CFP",
    relationship_type: "Individual Advisory", 
    assets_under_management: "$456,789.12",
    last_annual_review: "2024-06-01",
    next_scheduled_review: "2025-06-01",
    risk_tolerance: "Moderate Aggressive",
    investment_objective: "Growth and Income"
  }
];

// Mock portfolios data for each client
export const mockPortfolios = [
  {
    client_id: "client_001",
    albridge_account: "ALB_789456123",
    as_of_date: "2025-08-31",
    total_portfolio_value: 847392.18,
    asset_allocation: {
      "US Large Cap Equity": 35.2,
      "US Small Cap Equity": 12.8,
      "International Developed Equity": 15.7,
      "Emerging Markets Equity": 6.3,
      "Investment Grade Bonds": 22.4,
      "High Yield Bonds": 4.2,
      "Cash & Money Market": 3.4
    },
    performance_summary: {
      "Quarter-to-Date": 2.7,
      "Year-to-Date": 8.4,
      "1-Year": 12.1,
      "3-Year Annualized": 7.9,
      "Since Inception": 9.2
    }
  },
  {
    client_id: "client_002",
    albridge_account: "ALB_234567890",
    as_of_date: "2025-08-31",
    total_portfolio_value: 1234567.89,
    asset_allocation: {
      "US Large Cap Equity": 45.5,
      "US Small Cap Equity": 18.2,
      "International Developed Equity": 12.8,
      "Emerging Markets Equity": 8.7,
      "Investment Grade Bonds": 10.3,
      "High Yield Bonds": 2.8,
      "Cash & Money Market": 1.7
    },
    performance_summary: {
      "Quarter-to-Date": 4.2,
      "Year-to-Date": 12.8,
      "1-Year": 18.5,
      "3-Year Annualized": 11.3,
      "Since Inception": 13.7
    }
  },
  {
    client_id: "client_003",
    albridge_account: "ALB_345678901",
    as_of_date: "2025-08-31",
    total_portfolio_value: 2856402.34,
    asset_allocation: {
      "US Large Cap Equity": 25.8,
      "US Small Cap Equity": 5.2,
      "International Developed Equity": 8.7,
      "Emerging Markets Equity": 2.3,
      "Investment Grade Bonds": 45.6,
      "High Yield Bonds": 3.1,
      "Cash & Money Market": 9.3
    },
    performance_summary: {
      "Quarter-to-Date": 1.8,
      "Year-to-Date": 5.2,
      "1-Year": 7.8,
      "3-Year Annualized": 6.1,
      "Since Inception": 7.4
    }
  },
  {
    client_id: "client_004", 
    albridge_account: "ALB_456789012",
    as_of_date: "2025-08-31",
    total_portfolio_value: 456789.12,
    asset_allocation: {
      "US Large Cap Equity": 38.5,
      "US Small Cap Equity": 15.2,
      "International Developed Equity": 18.3,
      "Emerging Markets Equity": 7.8,
      "Investment Grade Bonds": 15.7,
      "High Yield Bonds": 2.9,
      "Cash & Money Market": 1.6
    },
    performance_summary: {
      "Quarter-to-Date": 3.1,
      "Year-to-Date": 9.7,
      "1-Year": 14.2,
      "3-Year Annualized": 8.9,
      "Since Inception": 10.4
    }
  }
];

export const mockMeetingNoteResult = {
  id: "note_001",
  client_information: {
    name: "Robert J. Smith",
    account_number: "RTS-789456123",
    meeting_date: "2025-09-10",
    meeting_type: "Quarterly Review",
    advisor: "Sarah Johnson, CFP"
  },
  discussion_topics: [
    {
      category: "Financial Goals Review",
      content: "Client confirmed retirement goal remains age 65 (15 years). Discussed increasing 401(k) contribution to maximum allowable limit due to recent salary increase.",
      regulatory_notes: "Goal reconfirmation documented per Investment Advisors Act requirements"
    },
    {
      category: "Risk Tolerance Assessment", 
      content: "Client maintains moderate risk tolerance. Recent market volatility has not changed investment timeline or comfort level. Confirmed continued appropriateness of 70/30 equity/bond allocation.",
      regulatory_notes: "Risk tolerance reassessment completed per firm policy"
    },
    {
      category: "Life Events",
      content: "Client mentioned daughter's college enrollment next year. Estimated additional expense of $25,000 annually for 4 years. Discussed 529 plan optimization.",
      regulatory_notes: "Material life event documented affecting financial planning recommendations"
    }
  ],
  recommendations_given: [
    {
      recommendation: "Increase 401(k) contribution from $15,000 to maximum $23,000 annually",
      rationale: "Recent salary increase provides capacity, maximizes tax-deferred growth opportunity",
      implementation: "Client to contact HR to adjust payroll deduction beginning next pay period",
      regulatory_basis: "Recommendation based on client's stated retirement timeline and risk tolerance"
    },
    {
      recommendation: "Establish additional 529 education savings plan with $5,000 initial funding",
      rationale: "Tax-advantaged college savings for daughter's education expenses",
      implementation: "Firm to prepare 529 application for client signature within 5 business days",
      regulatory_basis: "Education planning recommendation based on disclosed life event"
    }
  ],
  action_items: {
    client_responsibilities: [
      "Contact HR to increase 401(k) contribution by October 1, 2025",
      "Provide daughter's school information for 529 plan setup",
      "Review and sign 529 plan application within 7 days"
    ],
    firm_responsibilities: [
      "Prepare 529 education savings plan application by September 15, 2025",
      "Schedule follow-up call in 30 days to confirm 401(k) increase implementation",
      "Update client profile with new contribution levels and education expense timeline"
    ]
  },
  compliance_verification: {
    sec_requirements_met: true,
    fiduciary_standard_applied: true,
    suitability_documented: true,
    conflicts_of_interest: "None disclosed",
    fee_disclosure_current: true
  },
  audit_trail: {
    original_audio_duration: "47 minutes, 23 seconds",
    ai_processing_time: "2 minutes, 15 seconds", 
    ai_confidence_score: 96,
    human_reviewer: "Jennifer Walsh, CCO",
    review_date: "2025-09-10T16:45:00Z",
    approval_status: "approved",
    regulatory_retention_date: "2031-09-10"
  }
};

export const mockCRMIntegration = {
  client_profile: {
    redtail_id: "RT_12345",
    name: "Robert J. Smith",
    date_of_birth: "1975-03-15",
    account_opening_date: "2018-06-12", 
    primary_advisor: "Sarah Johnson, CFP",
    relationship_type: "Individual Advisory",
    assets_under_management: "$847,392.18",
    last_annual_review: "2024-09-15",
    next_scheduled_review: "2025-09-15",
    risk_tolerance: "Moderate",
    investment_objective: "Long-term Growth"
  },
  recent_activities: [
    {
      date: "2025-08-28",
      type: "Phone Call", 
      summary: "Discussed market volatility concerns, reassured client of long-term strategy",
      advisor: "Sarah Johnson"
    },
    {
      date: "2025-07-15",
      type: "Document Review",
      summary: "Client signed updated investment policy statement",
      advisor: "Sarah Johnson"
    }
  ]
};

export const mockPortfolioData = {
  albridge_account: "ALB_789456123",
  as_of_date: "2025-08-31",
  total_portfolio_value: 847392.18,
  asset_allocation: {
    "US Large Cap Equity": 35.2,
    "US Small Cap Equity": 12.8, 
    "International Developed Equity": 15.7,
    "Emerging Markets Equity": 6.3,
    "Investment Grade Bonds": 22.4,
    "High Yield Bonds": 4.2,
    "Cash & Money Market": 3.4
  },
  performance_summary: {
    "Quarter-to-Date": 2.7,
    "Year-to-Date": 8.4, 
    "1-Year": 12.1,
    "3-Year Annualized": 7.9,
    "Since Inception": 9.2
  },
  ai_analysis: {
    observations: [
      "Portfolio allocation closely aligns with moderate risk profile",
      "Performance tracking above target benchmark by 1.3% year-to-date",
      "Cash position appropriate for current market conditions"
    ],
    recommendations: [
      "Consider small rebalancing to target allocation (equity slightly overweight)",
      "Maintain current allocation given strong relative performance",
      "Monitor international exposure given recent currency fluctuations"
    ]
  }
};

export const mockComplianceDashboard = {
  pending_reviews: [
    {
      id: "review_001",
      client_name: "Robert J. Smith",
      meeting_date: "2025-09-10",
      ai_confidence: 96,
      priority: "normal",
      created: "2025-09-10T14:30:00Z",
      regulatory_flags: 0,
      requires_attention: false
    },
    {
      id: "review_002", 
      client_name: "Maria Gonzalez",
      meeting_date: "2025-09-09",
      ai_confidence: 78,
      priority: "high",
      created: "2025-09-09T16:15:00Z", 
      regulatory_flags: 1,
      requires_attention: true,
      flag_reason: "Complex investment recommendation requiring additional documentation"
    },
    {
      id: "review_003",
      client_name: "James Chen",
      meeting_date: "2025-09-09",
      ai_confidence: 92,
      priority: "normal",
      created: "2025-09-09T11:20:00Z",
      regulatory_flags: 0,
      requires_attention: false
    }
  ],
  audit_metrics: {
    notes_processed_today: 12,
    average_ai_confidence: 91,
    human_review_time_avg: "4m 23s",
    sec_compliance_rate: "100%",
    regulatory_flags_total: 3,
    approved_notes: 142,
    pending_approval: 5
  },
  security_status: {
    encryption_status: "Active - AES-256",
    last_security_scan: "2025-09-10T02:00:00Z",
    access_violations: 0,
    audit_trail_integrity: "Verified",
    data_retention_compliance: "Current"
  }
};

export const mockRecentMeetings = [
  {
    id: "meeting_001",
    client_name: "Robert J. Smith",
    date: "2025-09-10",
    type: "Quarterly Review",
    advisor: "Sarah Johnson, CFP",
    status: "approved",
    ai_confidence: 96,
    duration: "47m 23s"
  },
  {
    id: "meeting_002",
    client_name: "Maria Gonzalez", 
    date: "2025-09-09",
    type: "Annual Review",
    advisor: "Michael Chen, CFP",
    status: "pending",
    ai_confidence: 78,
    duration: "1h 15m"
  },
  {
    id: "meeting_003",
    client_name: "James Chen",
    date: "2025-09-09", 
    type: "Investment Review",
    advisor: "Sarah Johnson, CFP",
    status: "in_review",
    ai_confidence: 92,
    duration: "32m 18s"
  },
  {
    id: "meeting_004",
    client_name: "Lisa Rodriguez",
    date: "2025-09-08",
    type: "Risk Assessment",
    advisor: "David Park, CFP",
    status: "approved",
    ai_confidence: 88,
    duration: "28m 45s"
  }
];

// Flagged items mock data
export const mockFlaggedItems = [
  {
    id: "flagged_001",
    client_name: "Maria Gonzalez",
    meeting_date: "2025-09-09",
    ai_confidence: 78,
    priority: "high",
    created: "2025-09-09T16:15:00Z",
    flagged_date: "2025-09-09T16:45:00Z",
    flagged_by: "Jennifer Walsh, CCO",
    flag_reason: "Complex investment recommendation requiring additional documentation",
    flag_category: "Investment Recommendation",
    resolution_status: "pending",
    escalation_level: "supervisor",
    estimated_resolution_time: "2-3 business days"
  },
  {
    id: "flagged_002",
    client_name: "David Thompson",
    meeting_date: "2025-09-08",
    ai_confidence: 65,
    priority: "high",
    created: "2025-09-08T14:20:00Z",
    flagged_date: "2025-09-08T15:00:00Z",
    flagged_by: "Michael Chen, CFP",
    flag_reason: "Insufficient risk tolerance documentation for aggressive portfolio recommendation",
    flag_category: "Risk Assessment",
    resolution_status: "in_progress",
    escalation_level: "compliance_officer",
    estimated_resolution_time: "1-2 business days"
  }
];

// Security mock data
export const mockSecurityData = {
  security_metrics: {
    encryption_status: "Active - AES-256",
    last_security_scan: "2025-09-10T02:00:00Z",
    vulnerability_count: 0,
    access_violations_today: 0,
    failed_login_attempts: 3,
    active_sessions: 12,
    data_retention_compliance: "100%",
    audit_trail_integrity: "Verified"
  },
  recent_security_events: [
    {
      id: "sec_001",
      timestamp: "2025-09-10T09:15:00Z",
      event_type: "login_success",
      user: "sarah.johnson@firm.com",
      ip_address: "192.168.1.45",
      risk_level: "low",
      details: "Successful login from known device"
    },
    {
      id: "sec_002", 
      timestamp: "2025-09-10T08:30:00Z",
      event_type: "failed_login",
      user: "unknown@external.com",
      ip_address: "203.45.67.89",
      risk_level: "medium",
      details: "Failed login attempt - account not found"
    },
    {
      id: "sec_003",
      timestamp: "2025-09-10T07:45:00Z",
      event_type: "data_access",
      user: "jennifer.walsh@firm.com",
      ip_address: "192.168.1.22",
      risk_level: "low",
      details: "Accessed client portfolio data for compliance review"
    }
  ],
  compliance_monitoring: {
    sec_requirements_status: "compliant",
    data_encryption_compliance: "compliant", 
    record_retention_compliance: "compliant",
    access_control_compliance: "compliant",
    audit_trail_compliance: "compliant",
    last_compliance_check: "2025-09-10T06:00:00Z"
  },
  access_control: {
    total_users: 15,
    active_sessions: 12,
    failed_access_attempts: 3,
    privileged_access_reviews: 2,
    role_based_permissions: "enabled",
    two_factor_authentication: "enforced"
  }
};

export const mockTodayStats = {
  meetings_processed: 12,
  pending_reviews: 5,
  compliance_rate: 100,
  avg_confidence: 91,
  flagged_items: 2,
  approved_notes: 7
};