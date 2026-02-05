import React, { useState, useEffect, useCallback } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useParams, Link } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Shield, 
  Search, 
  AlertTriangle, 
  CheckCircle, 
  Download, 
  Clock, 
  Target,
  Activity,
  FileText,
  ChevronRight,
  ExternalLink,
  Loader2,
  Bug,
  Lock,
  Server,
  Code,
  Key,
  Database,
  Eye,
  AlertCircle,
  Info,
  History,
  Home as HomeIcon,
  Zap,
  User,
  Heart
} from "lucide-react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { ScrollArea } from "./components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { 
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./components/ui/tooltip";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "./components/ui/accordion";
import "./index.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Severity color mapping
const severityConfig = {
  Critical: { color: "bg-red-500/20 text-red-400 border-red-500/50", icon: AlertCircle },
  High: { color: "bg-orange-500/20 text-orange-400 border-orange-500/50", icon: AlertTriangle },
  Medium: { color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50", icon: AlertTriangle },
  Low: { color: "bg-blue-500/20 text-blue-400 border-blue-500/50", icon: Info },
  Info: { color: "bg-purple-500/20 text-purple-400 border-purple-500/50", icon: Info }
};

// OWASP category icons
const owaspIcons = {
  A01: Lock,
  A02: Server,
  A03: Database,
  A04: Key,
  A05: Code,
  A06: Bug,
  A07: Lock,
  A08: Database,
  A09: Eye,
  A10: AlertCircle
};

// Navigation Component
const Navigation = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="p-2 rounded-lg bg-[#00ff94]/10 border border-[#00ff94]/30 group-hover:border-[#00ff94]/60 transition-colors">
              <Shield className="w-6 h-6 text-[#00ff94]" />
            </div>
            <div>
              <h1 className="font-mono text-lg font-bold text-white tracking-tight">KiKi Pentester</h1>
              <p className="text-xs text-zinc-500">OWASP Top 10 2025</p>
            </div>
          </Link>
          <div className="flex items-center gap-4">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link to="/">
                    <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white hover:bg-white/5">
                      <HomeIcon className="w-5 h-5" />
                    </Button>
                  </Link>
                </TooltipTrigger>
                <TooltipContent>Home</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link to="/history">
                    <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white hover:bg-white/5">
                      <History className="w-5 h-5" />
                    </Button>
                  </Link>
                </TooltipTrigger>
                <TooltipContent>Scan History</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link to="/about">
                    <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white hover:bg-white/5">
                      <User className="w-5 h-5" />
                    </Button>
                  </Link>
                </TooltipTrigger>
                <TooltipContent>About</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Landing Page
const LandingPage = () => {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const startScan = async (e) => {
    e.preventDefault();
    if (!url.trim()) {
      toast.error("Please enter a valid URL");
      return;
    }

    // Add protocol if missing
    let targetUrl = url.trim();
    if (!targetUrl.startsWith("http://") && !targetUrl.startsWith("https://")) {
      targetUrl = "https://" + targetUrl;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/scans`, { target_url: targetUrl });
      toast.success("Scan initiated successfully!");
      navigate(`/scan/${response.data.id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to start scan");
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    { icon: Shield, title: "OWASP Top 10 2025", description: "Complete coverage of latest security risks" },
    { icon: Zap, title: "AI-Powered Analysis", description: "Claude Sonnet 4.5 powered insights" },
    { icon: FileText, title: "Detailed Reports", description: "Downloadable PDF vulnerability reports" }
  ];

  return (
    <div className="min-h-screen grid-bg relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#6e44ff]/5 via-transparent to-transparent pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#00ff94]/5 rounded-full blur-[120px] pointer-events-none" />
      
      <Navigation />
      
      <main className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16 fade-in">
            <Badge className="mb-6 bg-[#6e44ff]/20 text-[#6e44ff] border-[#6e44ff]/50 px-4 py-1.5">
              <Zap className="w-3 h-3 mr-1" />
              Powered by AI
            </Badge>
            <h1 className="font-mono text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 tracking-tight">
              KiKi Pentester
              <span className="text-[#00ff94] block mt-2">Security Scanner</span>
            </h1>
            <p className="text-zinc-400 text-base max-w-2xl mx-auto">
              Comprehensive web application security assessment based on OWASP Top 10 2025. 
              Active exploitation testing, AI-powered analysis, and detailed remediation guidance.
            </p>
          </div>

          {/* URL Input Terminal */}
          <div className="terminal max-w-2xl mx-auto mb-16 fade-in-delay-1 glow-primary">
            <div className="terminal-header">
              <div className="terminal-dot bg-red-500" />
              <div className="terminal-dot bg-yellow-500" />
              <div className="terminal-dot bg-green-500" />
              <span className="text-zinc-500 text-sm ml-2 font-mono">kiki_scanner.sh</span>
            </div>
            <form onSubmit={startScan} className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-[#00ff94] font-mono">$</span>
                <span className="text-zinc-500 font-mono">scan --target</span>
              </div>
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <Target className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                  <Input
                    data-testid="url-input"
                    type="text"
                    placeholder="https://example.com"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="pl-12 h-14 bg-black/50 border-zinc-800 text-white font-mono placeholder:text-zinc-600 focus:border-[#00ff94] focus:ring-[#00ff94]/20"
                  />
                </div>
                <Button 
                  data-testid="start-scan-btn"
                  type="submit" 
                  disabled={isLoading}
                  className="h-14 px-8 bg-[#00ff94] text-black font-mono font-semibold hover:bg-[#00ff94]/90 glow-primary btn-glow"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Initiating...
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5 mr-2" />
                      Scan
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 fade-in-delay-2">
            {features.map((feature, index) => (
              <Card 
                key={index}
                className="bg-[#0a0a0a]/80 border-zinc-800/50 card-hover"
              >
                <CardHeader>
                  <div className="p-3 rounded-lg bg-[#00ff94]/10 border border-[#00ff94]/20 w-fit mb-4">
                    <feature.icon className="w-6 h-6 text-[#00ff94]" />
                  </div>
                  <CardTitle className="font-mono text-white text-lg">{feature.title}</CardTitle>
                  <CardDescription className="text-zinc-500">{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>

          {/* OWASP Categories Preview */}
          <div className="mt-16 fade-in-delay-3">
            <h2 className="font-mono text-xl font-semibold text-white mb-6 text-center">
              OWASP Top 10 2025 Coverage
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"].map((id) => {
                const Icon = owaspIcons[id] || Shield;
                return (
                  <div 
                    key={id}
                    className="p-4 rounded-lg bg-[#0a0a0a]/80 border border-zinc-800/50 flex flex-col items-center gap-2 hover:border-[#6e44ff]/50 transition-colors"
                  >
                    <Icon className="w-5 h-5 text-[#6e44ff]" />
                    <span className="font-mono text-sm text-zinc-400">{id}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className="py-6 border-t border-zinc-800/50">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-zinc-500 text-sm">
            © 2026 KiKi Pentester. Created by <Link to="/about" className="text-[#00ff94] hover:underline">Shrinivas Natarajan</Link>
          </p>
        </div>
      </footer>
    </div>
  );
};

// Scan Dashboard Page
const ScanDashboard = () => {
  const { scanId } = useParams();
  const [scan, setScan] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const navigate = useNavigate();

  const fetchScan = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/scans/${scanId}`);
      setScan(response.data);
      setIsLoading(false);
    } catch (error) {
      toast.error("Failed to fetch scan data");
      navigate("/");
    }
  }, [scanId, navigate]);

  useEffect(() => {
    fetchScan();
    
    // Poll for updates if scan is not completed
    const interval = setInterval(() => {
      fetchScan();
    }, 3000);

    return () => clearInterval(interval);
  }, [fetchScan]);

  useEffect(() => {
    // Stop polling when scan is completed or failed
    if (scan?.status === "completed" || scan?.status === "failed") {
      return;
    }
  }, [scan?.status]);

  const downloadReport = async () => {
    setIsDownloading(true);
    try {
      // Method 1: Direct window open - most reliable for cross-browser downloads
      const downloadUrl = `${API}/scans/${scanId}/report`;
      
      // Create a hidden iframe to trigger download without leaving the page
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      iframe.src = downloadUrl;
      document.body.appendChild(iframe);
      
      // Also try the anchor method as fallback
      setTimeout(() => {
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `kiki_pentest_report_${scanId}.pdf`;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }, 500);
      
      // Cleanup iframe after download starts
      setTimeout(() => {
        if (iframe.parentNode) {
          document.body.removeChild(iframe);
        }
      }, 5000);
      
      toast.success("Report download started! Check your Downloads folder.");
    } catch (error) {
      console.error("Download error:", error);
      // Fallback: Open in new tab
      window.open(`${API}/scans/${scanId}/report`, '_blank');
      toast.info("Report opened in new tab. Right-click and Save As to download.");
    } finally {
      setIsDownloading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen grid-bg flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-[#00ff94] animate-spin mx-auto mb-4" />
          <p className="text-zinc-400 font-mono">Loading scan data...</p>
        </div>
      </div>
    );
  }

  const severityCounts = scan?.vulnerabilities?.reduce((acc, v) => {
    acc[v.severity] = (acc[v.severity] || 0) + 1;
    return acc;
  }, {}) || {};

  const owaspCounts = scan?.vulnerabilities?.reduce((acc, v) => {
    acc[v.owasp_id] = (acc[v.owasp_id] || 0) + 1;
    return acc;
  }, {}) || {};

  const isScanning = !["completed", "failed"].includes(scan?.status);

  return (
    <div className="min-h-screen grid-bg">
      {isScanning && <div className="scan-line" />}
      <Navigation />
      
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 fade-in">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Badge 
                  data-testid="scan-status-badge"
                  className={`font-mono ${
                    scan?.status === "completed" 
                      ? "bg-[#00ff94]/20 text-[#00ff94] border-[#00ff94]/50" 
                      : scan?.status === "failed"
                      ? "bg-red-500/20 text-red-400 border-red-500/50"
                      : "bg-yellow-500/20 text-yellow-400 border-yellow-500/50 pulse-glow"
                  }`}
                >
                  {scan?.status === "completed" ? (
                    <CheckCircle className="w-3 h-3 mr-1" />
                  ) : scan?.status === "failed" ? (
                    <AlertCircle className="w-3 h-3 mr-1" />
                  ) : (
                    <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                  )}
                  {scan?.status?.toUpperCase()}
                </Badge>
              </div>
              <h1 className="font-mono text-2xl font-bold text-white mb-1">Security Scan Results</h1>
              <p className="text-zinc-500 font-mono text-sm flex items-center gap-2">
                <Target className="w-4 h-4" />
                {scan?.target_url}
              </p>
            </div>
            {scan?.status === "completed" && (
              <Button 
                data-testid="download-report-btn"
                onClick={downloadReport}
                disabled={isDownloading}
                className="bg-[#00ff94] text-black font-mono font-semibold hover:bg-[#00ff94]/90 glow-primary"
              >
                {isDownloading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Download PDF Report
                  </>
                )}
              </Button>
            )}
          </div>

          {/* Progress Bar (while scanning) */}
          {isScanning && (
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 mb-8 fade-in">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-[#00ff94]/10">
                      <Activity className="w-5 h-5 text-[#00ff94] animate-pulse" />
                    </div>
                    <div>
                      <p className="font-mono text-white font-medium">Scanning in Progress</p>
                      <p className="text-zinc-500 text-sm">{scan?.status}</p>
                    </div>
                  </div>
                  <span className="font-mono text-[#00ff94] text-2xl font-bold">{scan?.progress}%</span>
                </div>
                <Progress value={scan?.progress || 0} className="h-2 bg-zinc-800" />
                <p className="text-zinc-500 text-sm mt-3 font-mono">
                  Pages crawled: {scan?.pages_crawled || 0} | Vulnerabilities found: {scan?.vulnerabilities_found || 0}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 card-hover fade-in">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-[#00ff94]/10">
                    <Search className="w-5 h-5 text-[#00ff94]" />
                  </div>
                  <span className="text-zinc-500 text-sm">Pages Scanned</span>
                </div>
                <p className="font-mono text-3xl font-bold text-white">{scan?.pages_crawled || 0}</p>
              </CardContent>
            </Card>

            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 card-hover fade-in-delay-1">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-red-500/10">
                    <Bug className="w-5 h-5 text-red-400" />
                  </div>
                  <span className="text-zinc-500 text-sm">Vulnerabilities</span>
                </div>
                <p className="font-mono text-3xl font-bold text-white">{scan?.vulnerabilities_found || 0}</p>
              </CardContent>
            </Card>

            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 card-hover fade-in-delay-2">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-red-500/10">
                    <AlertCircle className="w-5 h-5 text-red-400" />
                  </div>
                  <span className="text-zinc-500 text-sm">Critical/High</span>
                </div>
                <p className="font-mono text-3xl font-bold text-red-400">
                  {(severityCounts.Critical || 0) + (severityCounts.High || 0)}
                </p>
              </CardContent>
            </Card>

            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 card-hover fade-in-delay-3">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-[#6e44ff]/10">
                    <Clock className="w-5 h-5 text-[#6e44ff]" />
                  </div>
                  <span className="text-zinc-500 text-sm">Duration</span>
                </div>
                <p className="font-mono text-3xl font-bold text-white">
                  {scan?.completed_at 
                    ? Math.round((new Date(scan.completed_at) - new Date(scan.started_at)) / 1000) + "s"
                    : "—"
                  }
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Main Content Grid */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* Severity Breakdown */}
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 fade-in">
              <CardHeader>
                <CardTitle className="font-mono text-white flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-[#00ff94]" />
                  Severity Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {["Critical", "High", "Medium", "Low", "Info"].map((severity) => (
                    <div key={severity} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge className={`${severityConfig[severity].color} font-mono text-xs px-2 py-1`}>
                          {severity}
                        </Badge>
                      </div>
                      <span className="font-mono text-white font-semibold">
                        {severityCounts[severity] || 0}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* OWASP Coverage */}
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 fade-in-delay-1">
              <CardHeader>
                <CardTitle className="font-mono text-white flex items-center gap-2">
                  <Shield className="w-5 h-5 text-[#6e44ff]" />
                  OWASP Top 10 2025
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[280px]">
                  <div className="space-y-3 pr-4">
                    {["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"].map((id) => {
                      const Icon = owaspIcons[id] || Shield;
                      const count = owaspCounts[id] || 0;
                      return (
                        <div 
                          key={id}
                          className={`flex items-center justify-between p-3 rounded-lg border ${
                            count > 0 
                              ? "bg-[#6e44ff]/10 border-[#6e44ff]/30" 
                              : "bg-zinc-900/50 border-zinc-800"
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <Icon className={`w-4 h-4 ${count > 0 ? "text-[#6e44ff]" : "text-zinc-600"}`} />
                            <span className={`font-mono text-sm ${count > 0 ? "text-white" : "text-zinc-600"}`}>
                              {id}
                            </span>
                          </div>
                          <Badge 
                            variant="outline" 
                            className={`font-mono ${count > 0 ? "border-[#6e44ff] text-[#6e44ff]" : "border-zinc-700 text-zinc-600"}`}
                          >
                            {count}
                          </Badge>
                        </div>
                      );
                    })}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* AI Summary */}
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 glow-secondary fade-in-delay-2">
              <CardHeader>
                <CardTitle className="font-mono text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-[#6e44ff]" />
                  AI Analysis
                </CardTitle>
                <CardDescription className="text-zinc-500">
                  Powered by Claude Sonnet 4.5
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[240px]">
                  {scan?.ai_summary ? (
                    <div className="prose prose-sm prose-invert">
                      <p className="text-zinc-300 text-sm whitespace-pre-wrap leading-relaxed">
                        {scan.ai_summary}
                      </p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                      {isScanning ? (
                        <>
                          <Loader2 className="w-8 h-8 text-[#6e44ff] animate-spin mb-3" />
                          <p className="text-zinc-500 text-sm">AI analysis will be available after scan completes</p>
                        </>
                      ) : (
                        <p className="text-zinc-500 text-sm">No AI analysis available</p>
                      )}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Vulnerabilities List */}
          {scan?.vulnerabilities?.length > 0 && (
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 mt-8 fade-in">
              <CardHeader>
                <CardTitle className="font-mono text-white flex items-center gap-2">
                  <Bug className="w-5 h-5 text-red-400" />
                  Vulnerability Details
                </CardTitle>
                <CardDescription className="text-zinc-500">
                  {scan.vulnerabilities.length} vulnerabilities discovered
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="all" className="w-full">
                  <TabsList className="bg-zinc-900 border border-zinc-800 mb-6">
                    <TabsTrigger value="all" className="font-mono data-[state=active]:bg-[#00ff94] data-[state=active]:text-black">
                      All ({scan.vulnerabilities.length})
                    </TabsTrigger>
                    <TabsTrigger value="critical" className="font-mono data-[state=active]:bg-red-500 data-[state=active]:text-white">
                      Critical ({severityCounts.Critical || 0})
                    </TabsTrigger>
                    <TabsTrigger value="high" className="font-mono data-[state=active]:bg-orange-500 data-[state=active]:text-black">
                      High ({severityCounts.High || 0})
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="all">
                    <VulnerabilityList vulnerabilities={scan.vulnerabilities} />
                  </TabsContent>
                  <TabsContent value="critical">
                    <VulnerabilityList vulnerabilities={scan.vulnerabilities.filter(v => v.severity === "Critical")} />
                  </TabsContent>
                  <TabsContent value="high">
                    <VulnerabilityList vulnerabilities={scan.vulnerabilities.filter(v => v.severity === "High")} />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}

          {/* Crawled URLs */}
          {scan?.crawled_urls?.length > 0 && (
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 mt-8 fade-in">
              <CardHeader>
                <CardTitle className="font-mono text-white flex items-center gap-2">
                  <ExternalLink className="w-5 h-5 text-[#00ff94]" />
                  Crawled URLs
                </CardTitle>
                <CardDescription className="text-zinc-500">
                  {scan.crawled_urls.length} pages discovered and analyzed
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[200px]">
                  <div className="space-y-2 font-mono text-sm pr-4">
                    {scan.crawled_urls.map((url, index) => (
                      <div 
                        key={index}
                        className="flex items-center gap-2 p-2 rounded bg-zinc-900/50 border border-zinc-800 hover:border-[#00ff94]/30 transition-colors"
                      >
                        <ChevronRight className="w-4 h-4 text-[#00ff94]" />
                        <span className="text-zinc-400 truncate">{url}</span>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

// Vulnerability List Component
const VulnerabilityList = ({ vulnerabilities }) => {
  if (!vulnerabilities || vulnerabilities.length === 0) {
    return (
      <div className="text-center py-12">
        <CheckCircle className="w-12 h-12 text-[#00ff94] mx-auto mb-4" />
        <p className="text-zinc-400">No vulnerabilities found in this category</p>
      </div>
    );
  }

  return (
    <Accordion type="single" collapsible className="space-y-3">
      {vulnerabilities.map((vuln, index) => {
        const SeverityIcon = severityConfig[vuln.severity]?.icon || AlertTriangle;
        const OwaspIcon = owaspIcons[vuln.owasp_id] || Shield;
        
        return (
          <AccordionItem 
            key={vuln.id || index} 
            value={vuln.id || `vuln-${index}`}
            className="border border-zinc-800 rounded-lg bg-zinc-900/50 overflow-hidden"
          >
            <AccordionTrigger className="px-4 py-3 hover:no-underline hover:bg-zinc-800/50 [&[data-state=open]]:bg-zinc-800/50">
              <div className="flex items-center gap-4 text-left w-full">
                <Badge className={`${severityConfig[vuln.severity]?.color} font-mono text-xs px-2 py-1 shrink-0`}>
                  <SeverityIcon className="w-3 h-3 mr-1" />
                  {vuln.severity}
                </Badge>
                <Badge variant="outline" className="font-mono text-xs border-[#6e44ff] text-[#6e44ff] shrink-0">
                  <OwaspIcon className="w-3 h-3 mr-1" />
                  {vuln.owasp_id}
                </Badge>
                <span className="font-mono text-white text-sm truncate">{vuln.title}</span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-4 pb-4">
              <div className="space-y-4 pt-2">
                <div>
                  <h4 className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2">Description</h4>
                  <p className="text-zinc-300 text-sm">{vuln.description}</p>
                </div>
                
                <div>
                  <h4 className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2">Affected URL</h4>
                  <p className="text-[#00ff94] text-sm font-mono break-all">{vuln.url}</p>
                </div>
                
                {vuln.evidence && (
                  <div>
                    <h4 className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2">Evidence</h4>
                    <div className="code-block">
                      <code className="text-zinc-300">{vuln.evidence}</code>
                    </div>
                  </div>
                )}
                
                {vuln.remediation && (
                  <div>
                    <h4 className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2">Remediation</h4>
                    <p className="text-zinc-300 text-sm bg-[#00ff94]/5 border border-[#00ff94]/20 rounded-lg p-3">
                      {vuln.remediation}
                    </p>
                  </div>
                )}
                
                {vuln.ai_analysis && (
                  <div>
                    <h4 className="text-xs font-mono text-zinc-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <Zap className="w-3 h-3 text-[#6e44ff]" />
                      AI Analysis
                    </h4>
                    <p className="text-zinc-300 text-sm bg-[#6e44ff]/5 border border-[#6e44ff]/20 rounded-lg p-3">
                      {vuln.ai_analysis}
                    </p>
                  </div>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>
        );
      })}
    </Accordion>
  );
};

// Scan History Page
const HistoryPage = () => {
  const [scans, setScans] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchScans = async () => {
      try {
        const response = await axios.get(`${API}/scans`);
        setScans(response.data);
      } catch (error) {
        toast.error("Failed to fetch scan history");
      } finally {
        setIsLoading(false);
      }
    };
    fetchScans();
  }, []);

  const deleteScan = async (scanId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/scans/${scanId}`);
      setScans(scans.filter(s => s.id !== scanId));
      toast.success("Scan deleted successfully");
    } catch (error) {
      toast.error("Failed to delete scan");
    }
  };

  return (
    <div className="min-h-screen grid-bg">
      <Navigation />
      
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="mb-8 fade-in">
            <h1 className="font-mono text-3xl font-bold text-white mb-2">Scan History</h1>
            <p className="text-zinc-500">View and manage your previous security scans</p>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-[#00ff94] animate-spin" />
            </div>
          ) : scans.length === 0 ? (
            <Card className="bg-[#0a0a0a]/80 border-zinc-800/50">
              <CardContent className="py-20 text-center">
                <Search className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
                <h3 className="font-mono text-xl text-white mb-2">No scans yet</h3>
                <p className="text-zinc-500 mb-6">Start your first security scan to see results here</p>
                <Button 
                  onClick={() => navigate("/")}
                  className="bg-[#00ff94] text-black font-mono hover:bg-[#00ff94]/90"
                >
                  Start New Scan
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {scans.map((scan, index) => (
                <Card 
                  key={scan.id}
                  data-testid={`scan-history-item-${index}`}
                  className="bg-[#0a0a0a]/80 border-zinc-800/50 card-hover cursor-pointer fade-in"
                  style={{ animationDelay: `${index * 0.1}s` }}
                  onClick={() => navigate(`/scan/${scan.id}`)}
                >
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-lg ${
                          scan.status === "completed" 
                            ? "bg-[#00ff94]/10" 
                            : scan.status === "failed"
                            ? "bg-red-500/10"
                            : "bg-yellow-500/10"
                        }`}>
                          {scan.status === "completed" ? (
                            <CheckCircle className="w-6 h-6 text-[#00ff94]" />
                          ) : scan.status === "failed" ? (
                            <AlertCircle className="w-6 h-6 text-red-400" />
                          ) : (
                            <Loader2 className="w-6 h-6 text-yellow-400 animate-spin" />
                          )}
                        </div>
                        <div>
                          <p className="font-mono text-white font-medium mb-1 flex items-center gap-2">
                            <Target className="w-4 h-4 text-zinc-500" />
                            {scan.target_url}
                          </p>
                          <div className="flex items-center gap-4 text-sm text-zinc-500">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {new Date(scan.started_at).toLocaleString()}
                            </span>
                            <span className="flex items-center gap-1">
                              <Bug className="w-3 h-3" />
                              {scan.vulnerabilities_found} vulnerabilities
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className={`font-mono ${
                          scan.status === "completed"
                            ? "bg-[#00ff94]/20 text-[#00ff94] border-[#00ff94]/50"
                            : scan.status === "failed"
                            ? "bg-red-500/20 text-red-400 border-red-500/50"
                            : "bg-yellow-500/20 text-yellow-400 border-yellow-500/50"
                        }`}>
                          {scan.status}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-zinc-500 hover:text-red-400 hover:bg-red-500/10"
                          onClick={(e) => deleteScan(scan.id, e)}
                        >
                          Delete
                        </Button>
                        <ChevronRight className="w-5 h-5 text-zinc-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

// About Page
const AboutPage = () => {
  return (
    <div className="min-h-screen grid-bg">
      <Navigation />
      
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-3xl mx-auto">
          {/* Hero */}
          <div className="text-center mb-12 fade-in">
            <div className="inline-flex p-4 rounded-2xl bg-[#00ff94]/10 border border-[#00ff94]/30 mb-6">
              <Shield className="w-16 h-16 text-[#00ff94]" />
            </div>
            <h1 className="font-mono text-4xl font-bold text-white mb-4">KiKi Pentester</h1>
            <p className="text-zinc-400 text-lg">Automated Web Application Security Scanner</p>
          </div>

          {/* About Card */}
          <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 mb-8 fade-in-delay-1">
            <CardHeader>
              <CardTitle className="font-mono text-white flex items-center gap-2">
                <Info className="w-5 h-5 text-[#6e44ff]" />
                About This Application
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-zinc-300">
              <p>
                KiKi Pentester is a comprehensive automated web application penetration testing tool 
                designed to identify security vulnerabilities based on the OWASP Top 10 2025 framework.
              </p>
              <p>
                The tool performs both Static Application Security Testing (SAST) and Dynamic Application 
                Security Testing (DAST) to provide thorough security assessments of web applications.
              </p>
              <p>
                Powered by Claude Sonnet 4.5 AI, KiKi Pentester provides intelligent vulnerability 
                analysis and actionable remediation guidance to help developers and security professionals 
                secure their applications.
              </p>
            </CardContent>
          </Card>

          {/* Features */}
          <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 mb-8 fade-in-delay-2">
            <CardHeader>
              <CardTitle className="font-mono text-white flex items-center gap-2">
                <Zap className="w-5 h-5 text-[#00ff94]" />
                Key Features
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-zinc-300">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#00ff94] shrink-0 mt-0.5" />
                  <span>Complete OWASP Top 10 2025 vulnerability coverage</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#00ff94] shrink-0 mt-0.5" />
                  <span>Automated web crawling and page discovery</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#00ff94] shrink-0 mt-0.5" />
                  <span>AI-powered security analysis and remediation suggestions</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#00ff94] shrink-0 mt-0.5" />
                  <span>Detailed PDF vulnerability reports</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-[#00ff94] shrink-0 mt-0.5" />
                  <span>Real-time scan progress tracking</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Owner/Creator */}
          <Card className="bg-[#0a0a0a]/80 border-zinc-800/50 glow-secondary fade-in-delay-3">
            <CardHeader>
              <CardTitle className="font-mono text-white flex items-center gap-2">
                <User className="w-5 h-5 text-[#6e44ff]" />
                Creator & Owner
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className="p-4 rounded-full bg-[#6e44ff]/10 border border-[#6e44ff]/30">
                  <User className="w-12 h-12 text-[#6e44ff]" />
                </div>
                <div>
                  <h3 className="font-mono text-2xl font-bold text-white mb-2">Shrinivas Natarajan</h3>
                  <p className="text-zinc-400 mb-3">Creator, Owner & Lead Developer</p>
                  <p className="text-zinc-500 text-sm">
                    KiKi Pentester is owned and maintained by Shrinivas Natarajan. 
                    All rights reserved © 2026.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="text-center mt-12 fade-in-delay-3">
            <p className="text-zinc-500 text-sm flex items-center justify-center gap-2">
              Made with <Heart className="w-4 h-4 text-red-400" /> by Shrinivas Natarajan
            </p>
            <p className="text-zinc-600 text-xs mt-2">
              www.kikipentester.com
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

// Main App
function App() {
  return (
    <div className="App dark">
      <Toaster 
        position="top-right" 
        toastOptions={{
          style: {
            background: '#0a0a0a',
            border: '1px solid #27272a',
            color: '#fff',
          },
        }}
      />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/scan/:scanId" element={<ScanDashboard />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
