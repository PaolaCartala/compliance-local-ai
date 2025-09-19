import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { APIProvider } from "./contexts/APIContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { MainLayout } from "./layout/MainLayout";
import Dashboard from "./pages/Dashboard";
import ProcessNotes from "./pages/ProcessNotes";
import ReviewQueue from "./pages/ReviewQueue";
import PendingReviews from "./pages/PendingReviews";
import FlaggedItems from "./pages/FlaggedItems";
import Security from "./pages/Security";
import Settings from "./pages/Settings";
import AuditTrail from "./pages/AuditTrail";
import Chat from "./pages/Chat";
import ClientIntegration from "./pages/ClientIntegration";
import FillTemplates from "./pages/FillTemplates";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import UpcomingFeatures from "./pages/UpcomingFeatures";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <APIProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/*" element={
                <ProtectedRoute>
                  <MainLayout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/process" element={<ProcessNotes />} />
                      <Route path="/review" element={<ReviewQueue />} />
                      <Route path="/review/pending" element={<PendingReviews />} />
                      <Route path="/review/flagged" element={<FlaggedItems />} />
                      <Route path="/security" element={<Security />} />
                      <Route path="/settings" element={<Settings />} />
                      <Route path="/audit" element={<AuditTrail />} />
                      <Route path="/chat" element={<Chat />} />
                      <Route path="/clients" element={<ClientIntegration />} />
                      <Route path="/features" element={<UpcomingFeatures />} />
                      <Route path="/templates" element={<FillTemplates />} />
                      {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </MainLayout>
                </ProtectedRoute>
              } />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </APIProvider>
  </QueryClientProvider>
);

export default App;
