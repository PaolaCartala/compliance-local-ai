import { CheckCircle, AlertCircle, XCircle, Clock, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

interface ComplianceStatusProps {
  status: "approved" | "pending" | "flagged" | "in_review" | "secure";
  children?: React.ReactNode;
  showIcon?: boolean;
  size?: "sm" | "default" | "lg";
  className?: string;
}

const statusConfig = {
  approved: {
    icon: CheckCircle,
    className: "compliance-approved",
    text: "Approved"
  },
  pending: {
    icon: Clock,
    className: "compliance-pending",
    text: "Pending Review"
  },
  flagged: {
    icon: XCircle,
    className: "compliance-flagged",
    text: "Compliance Flag"
  },
  in_review: {
    icon: AlertCircle,
    className: "compliance-pending",
    text: "In Review"
  },
  secure: {
    icon: Shield,
    className: "compliance-approved",
    text: "Secure"
  }
};

export function ComplianceStatus({ 
  status, 
  children, 
  showIcon = true, 
  size = "default",
  className 
}: ComplianceStatusProps) {
  const config = statusConfig[status];
  const Icon = config.icon;
  
  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    default: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base"
  };
  
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 rounded-full font-medium transition-all",
      config.className,
      sizeClasses[size],
      className
    )}>
      {showIcon && <Icon className="w-4 h-4" />}
      {children || config.text}
    </span>
  );
}