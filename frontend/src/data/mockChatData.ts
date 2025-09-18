import { CustomGPT, Thread, Message, SystemPromptTemplate } from "@/types/chat";

export const mockCustomGPTs: CustomGPT[] = [
  {
    id: "gpt_crm_001",
    name: "CRM Assistant",
    description: "Specialized in client relationship management and Redtail CRM integration",
    systemPrompt: "You are a specialized CRM assistant for financial advisors. You help manage client relationships, track communications, and ensure proper documentation for SEC compliance. Always prioritize client confidentiality and regulatory requirements.",
    specialization: "crm",
    color: "blue",
    icon: "Users",
    mcpToolsEnabled: {
      redtailCRM: true,
      albridgePortfolio: false,
      blackDiamond: false
    },
    isActive: true,
    createdAt: "2025-09-01T09:00:00Z",
    updatedAt: "2025-09-05T14:30:00Z"
  },
  {
    id: "gpt_portfolio_001", 
    name: "Portfolio Analyzer",
    description: "Investment analysis and portfolio management with Albridge integration",
    systemPrompt: "You are a specialized portfolio analysis assistant for wealth management. You analyze investment portfolios, provide performance insights, and make SEC-compliant investment recommendations based on client risk tolerance and objectives.",
    specialization: "portfolio",
    color: "green",
    icon: "TrendingUp",
    mcpToolsEnabled: {
      redtailCRM: false,
      albridgePortfolio: true,
      blackDiamond: false
    },
    isActive: true,
    createdAt: "2025-09-01T09:15:00Z",
    updatedAt: "2025-09-08T11:20:00Z"
  },
  {
    id: "gpt_compliance_001",
    name: "Compliance Monitor", 
    description: "SEC compliance oversight and regulatory guidance",
    systemPrompt: "You are a specialized compliance assistant for financial advisory firms. You ensure all communications, recommendations, and documentation meet SEC and FINRA requirements. You flag potential compliance issues and provide regulatory guidance.",
    specialization: "compliance",
    color: "red",
    icon: "Shield",
    mcpToolsEnabled: {
      redtailCRM: true,
      albridgePortfolio: true,
      blackDiamond: false
    },
    isActive: true,
    createdAt: "2025-09-01T09:30:00Z",
    updatedAt: "2025-09-07T16:45:00Z"
  },
  {
    id: "gpt_general_001",
    name: "General Advisor",
    description: "Comprehensive financial planning and advisory assistance",
    systemPrompt: "You are a comprehensive financial planning assistant. You provide holistic financial advice covering investments, retirement planning, tax strategies, and estate planning while maintaining strict SEC compliance standards.",
    specialization: "general",
    color: "purple",
    icon: "Brain", 
    mcpToolsEnabled: {
      redtailCRM: true,
      albridgePortfolio: true,
      blackDiamond: true
    },
    isActive: true,
    createdAt: "2025-09-01T09:45:00Z",
    updatedAt: "2025-09-09T10:15:00Z"
  }
];

export const mockThreads: Thread[] = [
  {
    id: "thread_001",
    title: "Robert J. Smith - Portfolio Review",
    customGPTId: "gpt_portfolio_001",
    createdAt: "2025-09-10T09:30:00Z",
    updatedAt: "2025-09-10T11:45:00Z",
    lastMessage: "Based on the portfolio analysis, I recommend a slight rebalancing to reduce equity overweight...",
    messageCount: 12,
    isArchived: false,
    tags: ["quarterly-review", "rebalancing"]
  },
  {
    id: "thread_002", 
    title: "Maria Gonzalez - CRM Update",
    customGPTId: "gpt_crm_001",
    createdAt: "2025-09-09T14:20:00Z",
    updatedAt: "2025-09-09T16:10:00Z",
    lastMessage: "I've updated the client profile with the new contact information and documented today's call.",
    messageCount: 8,
    isArchived: false,
    tags: ["profile-update", "contact-change"]
  },
  {
    id: "thread_003",
    title: "Compliance Review - Q3 2025",
    customGPTId: "gpt_compliance_001", 
    createdAt: "2025-09-08T10:00:00Z",
    updatedAt: "2025-09-10T08:30:00Z",
    lastMessage: "All client communications this quarter meet SEC documentation requirements. No violations detected.",
    messageCount: 25,
    isArchived: false,
    tags: ["quarterly-review", "sec-compliance"]
  },
  {
    id: "thread_004",
    title: "James Chen - Retirement Planning",
    customGPTId: "gpt_general_001",
    createdAt: "2025-09-07T15:30:00Z", 
    updatedAt: "2025-09-08T12:20:00Z",
    lastMessage: "The 401(k) optimization strategy looks solid. Consider also exploring backdoor Roth IRA options.",
    messageCount: 18,
    isArchived: false,
    tags: ["retirement", "401k", "tax-strategy"]
  },
  {
    id: "thread_005",
    title: "Tax Loss Harvesting Analysis",
    customGPTId: "gpt_portfolio_001",
    createdAt: "2025-09-06T11:15:00Z",
    updatedAt: "2025-09-06T14:30:00Z", 
    lastMessage: "Identified $15,000 in potential tax loss harvesting opportunities for year-end.",
    messageCount: 7,
    isArchived: true,
    tags: ["tax-strategy", "year-end-planning"]
  }
];

export const mockMessages: Message[] = [
  {
    id: "msg_001",
    threadId: "thread_001", 
    content: "Can you analyze Robert Smith's current portfolio performance and recommend any adjustments?",
    role: "user",
    timestamp: "2025-09-10T09:30:00Z",
    attachments: [
      {
        id: "file_001",
        name: "robert_smith_portfolio.xlsx",
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        size: 245760,
        url: "/uploads/robert_smith_portfolio.xlsx",
        uploadedAt: "2025-09-10T09:29:00Z"
      }
    ]
  },
  {
    id: "msg_002",
    threadId: "thread_001",
    content: "I've analyzed Robert Smith's portfolio data from the Excel file. Here's my assessment:\n\n**Current Allocation Analysis:**\n- Large Cap Equity: 35.2% (target: 30-35%)\n- Small Cap Equity: 12.8% (target: 10-15%)\n- International Equity: 22.0% (target: 15-20%)\n- Bonds: 26.6% (target: 25-30%)\n- Cash: 3.4% (target: 5%)\n\n**Key Findings:**\n1. Portfolio is slightly overweight in international equity (+2-7%)\n2. Cash position is below target allocation\n3. Overall performance is strong at 8.4% YTD\n\n**Recommendations:**\n1. Reduce international equity by $25,000\n2. Increase cash position to 5% of portfolio\n3. Consider tax-loss harvesting in underperforming international positions\n\n**Compliance Note:** All recommendations align with client's moderate risk tolerance documented in annual review.",
    role: "assistant",
    timestamp: "2025-09-10T09:35:00Z",
    customGPTId: "gpt_portfolio_001",
    mcpToolInteractions: [
      {
        toolName: "albridge-portfolio",
        action: "fetch_portfolio_data", 
        data: { clientId: "RT_12345", asOfDate: "2025-09-10" },
        timestamp: "2025-09-10T09:34:00Z",
        success: true
      }
    ]
  }
];

export const mockSystemPromptTemplates: SystemPromptTemplate[] = [
  {
    id: "template_001",
    name: "CRM Specialist",
    description: "Client relationship management and communication tracking",
    specialization: "crm",
    prompt: "You are a specialized CRM assistant for financial advisors. You help manage client relationships, track communications, schedule follow-ups, and ensure proper documentation for SEC compliance. Always prioritize client confidentiality and regulatory requirements. When accessing client data, verify permissions and log all interactions for audit trails.",
    mcpToolsRecommended: {
      redtailCRM: true,
      albridgePortfolio: false,
      blackDiamond: false
    }
  },
  {
    id: "template_002", 
    name: "Portfolio Manager",
    description: "Investment analysis and portfolio optimization",
    specialization: "portfolio",
    prompt: "You are a specialized portfolio analysis assistant for wealth management. You analyze investment portfolios, provide performance insights, and make SEC-compliant investment recommendations based on client risk tolerance and objectives. Always consider tax implications, diversification, and regulatory requirements in your analysis.",
    mcpToolsRecommended: {
      redtailCRM: false,
      albridgePortfolio: true,
      blackDiamond: false
    }
  },
  {
    id: "template_003",
    name: "Compliance Officer",
    description: "SEC compliance monitoring and regulatory guidance", 
    specialization: "compliance",
    prompt: "You are a specialized compliance assistant for financial advisory firms. You ensure all communications, recommendations, and documentation meet SEC and FINRA requirements. You flag potential compliance issues, provide regulatory guidance, and maintain audit trails. Always err on the side of caution when interpreting regulations.",
    mcpToolsRecommended: {
      redtailCRM: true,
      albridgePortfolio: true, 
      blackDiamond: false
    }
  },
  {
    id: "template_004",
    name: "Retirement Planner",
    description: "Specialized in retirement and tax-advantaged planning",
    specialization: "retirement",
    prompt: "You are a specialized retirement planning assistant. You help clients optimize their retirement savings strategies, including 401(k), IRA, Roth conversions, and Social Security planning. You provide tax-efficient strategies while ensuring SEC compliance and proper documentation.",
    mcpToolsRecommended: {
      redtailCRM: true,
      albridgePortfolio: true,
      blackDiamond: true
    }
  },
  {
    id: "template_005",
    name: "Tax Strategist", 
    description: "Tax-efficient investment and planning strategies",
    specialization: "tax",
    prompt: "You are a specialized tax strategy assistant for financial planning. You help optimize tax efficiency through investment selection, asset location, tax-loss harvesting, and strategic planning. Always consider current tax law and coordinate with client's tax professional.",
    mcpToolsRecommended: {
      redtailCRM: false,
      albridgePortfolio: true,
      blackDiamond: true
    }
  }
];