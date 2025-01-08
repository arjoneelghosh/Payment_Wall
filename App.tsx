
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Questionnaire from "./pages/Questionnaire";
import DocumentUpload from "./pages/DocumentUpload";
import LoanStatus from "./pages/LoanStatus";
import NotFound from "./pages/NotFound";
import { AuthProvider } from "./context/AuthContext";
import { LoanProvider } from "./context/LoanContext";
import CameraPreview from "./components/ui-elements/CameraPreview";

const queryClient = new QueryClient();

// Created a separate component for CameraPreview to enable route-based conditional rendering
const ConditionalCameraPreview = () => {
  const location = useLocation();
  
  // Only show camera preview on specific pages where it's needed
  // Exclude document upload, landing page, and loan status pages
  if (
    location.pathname === "/document-upload" || 
    location.pathname === "/" || 
    location.pathname === "/loan-status"
  ) {
    return null;
  }
  
  return <CameraPreview />;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <LoanProvider>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<Login />} />
              <Route path="/questionnaire" element={<Questionnaire />} />
              <Route path="/document-upload" element={<DocumentUpload />} />
              <Route path="/loan-status" element={<LoanStatus />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
            <ConditionalCameraPreview />
          </LoanProvider>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
