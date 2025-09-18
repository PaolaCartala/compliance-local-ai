import { useState } from "react";
import { LayoutDashboard, FileText, CheckSquare, MessageSquare, Users, Shield, Settings, Upload, Eye, AlertTriangle, File } from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarTrigger, useSidebar, SidebarHeader, SidebarFooter } from "@/components/ui/sidebar";
import { ComplianceStatus } from "./ComplianceStatus";
const mainItems = [{
  title: "Chat",
  url: "/chat",
  icon: MessageSquare
}, {
  title: "Process Notes",
  url: "/process",
  icon: Upload
}, {
  title: "Fill Templates",
  url: "/templates",
  icon: File
}];

const dashboardItems = [{
  title: "Dashboard",
  url: "/",
  icon: LayoutDashboard
}];

const complianceItems = [{
  title: "Audit Trail",
  url: "/audit",
  icon: Eye
}, {
  title: "Security",
  url: "/security",
  icon: Shield
}];

const upcomingItems = [{
  title: "Upcoming Features",
  url: "/features",
  icon: Users
}];

const reviewItems = [{
  title: "Review Queue",
  url: "/review",
  icon: CheckSquare
}, {
  title: "Pending Reviews",
  url: "/review/pending",
  icon: AlertTriangle,
  count: 5
}, {
  title: "Flagged Items",
  url: "/review/flagged",
  icon: Shield,
  count: 2
}];
const adminItems = [{
  title: "Settings",
  url: "/settings",
  icon: Settings
}];
export function AppSidebar() {
  const {
    state
  } = useSidebar();
  const location = useLocation();
  const currentPath = location.pathname;
  const collapsed = state === "collapsed";
  const isActive = (path: string) => {
    if (path === "/") return currentPath === "/";
    return currentPath.startsWith(path);
  };
  const getNavClass = (path: string) => isActive(path) ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium border-r-2 border-primary" : "hover:bg-sidebar-accent/50 text-sidebar-foreground";
  return <Sidebar className="border-r border-sidebar-border">
      <SidebarHeader className="border-b border-sidebar-border p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <img src="/lovable-uploads/5cfbb876-140b-4ac9-bc63-84e5fd416aa6.png" className="w-5 h-5" alt="Baker Group Logo" />
          </div>
          {!collapsed && <div>
              <h2 className="text-sm font-semibold text-sidebar-foreground">SEC Compliance AI</h2>
              <p className="text-xs text-sidebar-foreground/70">The Baker Group</p>
            </div>}
        </div>
      </SidebarHeader>

      <SidebarContent className="p-2 space-y-4">
        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70 text-xs font-medium uppercase tracking-wider">
            {!collapsed ? "Home" : ""}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {dashboardItems.map(item => <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} className={getNavClass(item.url)}>
                      <item.icon className="w-5 h-5" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70 text-xs font-medium uppercase tracking-wider">
            {!collapsed ? "Main Navigation" : ""}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map(item => <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} className={getNavClass(item.url)}>
                      <item.icon className="w-5 h-5" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70 text-xs font-medium uppercase tracking-wider">
            {!collapsed ? "Review Queue" : ""}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {reviewItems.map(item => <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} className={getNavClass(item.url)}>
                      <item.icon className="w-5 h-5" />
                      {!collapsed && <div className="flex items-center justify-between w-full">
                          <span>{item.title}</span>
                          {item.count && <span className="bg-warning text-warning-foreground px-2 py-0.5 rounded-full text-xs font-medium">
                              {item.count}
                            </span>}
                        </div>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70 text-xs font-medium uppercase tracking-wider">
            {!collapsed ? "Compliance" : ""}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {complianceItems.map(item => <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} className={getNavClass(item.url)}>
                      <item.icon className="w-5 h-5" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70 text-xs font-medium uppercase tracking-wider">
            {!collapsed ? "Upcoming Features" : ""}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {upcomingItems.map(item => <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} className={getNavClass(item.url)}>
                      <item.icon className="w-5 h-5" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/70 text-xs font-medium uppercase tracking-wider">
            {!collapsed ? "Administration" : ""}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {adminItems.map(item => <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink to={item.url} className={getNavClass(item.url)}>
                      <item.icon className="w-5 h-5" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>)}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-4">
        {!collapsed && <div className="space-y-2">
            <ComplianceStatus status="secure" size="sm" />
            <p className="text-xs text-sidebar-foreground/70">
              AES-256 Encrypted
            </p>
          </div>}
      </SidebarFooter>
    </Sidebar>;
}