import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface FinancialMetricProps {
  label: string;
  value: string | number;
  change?: number;
  changeType?: "percentage" | "absolute";
  trend?: "up" | "down" | "neutral";
  format?: "currency" | "percentage" | "number";
  size?: "sm" | "default" | "lg";
  className?: string;
}

export function FinancialMetric({
  label,
  value,
  change,
  changeType = "percentage",
  trend,
  format = "number",
  size = "default",
  className
}: FinancialMetricProps) {
  
  const formatValue = (val: string | number) => {
    if (format === "currency" && typeof val === "number") {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(val);
    }
    
    if (format === "percentage" && typeof val === "number") {
      return `${val}%`;
    }
    
    return val;
  };

  const getTrendColor = (trendType?: "up" | "down" | "neutral") => {
    switch (trendType) {
      case "up":
        return "status-positive";
      case "down":
        return "status-negative";
      default:
        return "status-neutral";
    }
  };

  const getTrendIcon = (trendType?: "up" | "down" | "neutral") => {
    switch (trendType) {
      case "up":
        return TrendingUp;
      case "down":
        return TrendingDown;
      default:
        return Minus;
    }
  };

  const sizeClasses = {
    sm: {
      value: "text-lg font-semibold",
      label: "text-xs text-muted-foreground",
      change: "text-xs"
    },
    default: {
      value: "text-2xl font-bold",
      label: "text-sm text-muted-foreground",
      change: "text-sm"
    },
    lg: {
      value: "text-3xl font-bold",
      label: "text-base text-muted-foreground",
      change: "text-base"
    }
  };

  const TrendIcon = getTrendIcon(trend);

  return (
    <div className={cn("space-y-1", className)}>
      <p className={sizeClasses[size].label}>{label}</p>
      <div className="flex items-end gap-2">
        <span className={cn("font-mono", sizeClasses[size].value)}>
          {formatValue(value)}
        </span>
        {change !== undefined && (
          <div className={cn(
            "flex items-center gap-1",
            sizeClasses[size].change,
            getTrendColor(trend)
          )}>
            <TrendIcon className="w-3 h-3" />
            <span className="font-medium">
              {changeType === "percentage" ? `${change}%` : change}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}