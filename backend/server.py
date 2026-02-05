from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
import aiohttp
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Screenshot capture
async def capture_screenshot(url: str, output_path: str) -> bool:
    """Capture screenshot of a URL using Playwright"""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.screenshot(path=output_path, full_page=False)
            await browser.close()
            return True
    except Exception as e:
        logger.error(f"Screenshot capture failed for {url}: {e}")
        return False

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, scan_id: str):
        await websocket.accept()
        self.active_connections[scan_id] = websocket

    def disconnect(self, scan_id: str):
        if scan_id in self.active_connections:
            del self.active_connections[scan_id]

    async def send_update(self, scan_id: str, message: dict):
        if scan_id in self.active_connections:
            try:
                await self.active_connections[scan_id].send_json(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic Models
class ScanCreate(BaseModel):
    target_url: str

class Vulnerability(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    owasp_id: str
    title: str
    description: str
    severity: str  # Critical, High, Medium, Low, Info
    evidence: Optional[str] = None
    url: str
    remediation: Optional[str] = None
    ai_analysis: Optional[str] = None

class Scan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_url: str
    status: str = "pending"  # pending, crawling, scanning, analyzing, completed, failed
    progress: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    pages_crawled: int = 0
    vulnerabilities_found: int = 0
    crawled_urls: List[str] = []
    vulnerabilities: List[Vulnerability] = []
    ai_summary: Optional[str] = None
    report_path: Optional[str] = None

class ScanResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    target_url: str
    status: str
    progress: int
    started_at: str
    completed_at: Optional[str] = None
    pages_crawled: int
    vulnerabilities_found: int
    crawled_urls: List[str]
    vulnerabilities: List[dict]
    ai_summary: Optional[str] = None
    report_path: Optional[str] = None

# OWASP Top 10 2025 Categories
OWASP_CATEGORIES = {
    "A01": {"name": "Broken Access Control", "description": "Restrictions on authenticated users are not properly enforced"},
    "A02": {"name": "Security Misconfiguration", "description": "Missing appropriate security hardening across the application stack"},
    "A03": {"name": "Software Supply Chain Failures", "description": "Risks from untrusted third-party components and dependencies"},
    "A04": {"name": "Cryptographic Failures", "description": "Failures related to cryptography which often lead to exposure of sensitive data"},
    "A05": {"name": "Injection", "description": "User-supplied data is not validated, filtered, or sanitized by the application"},
    "A06": {"name": "Insecure Design", "description": "Missing or ineffective control design"},
    "A07": {"name": "Authentication Failures", "description": "Confirmation of the user's identity and session management issues"},
    "A08": {"name": "Software or Data Integrity Failures", "description": "Code and infrastructure that does not protect against integrity violations"},
    "A09": {"name": "Logging & Alerting Failures", "description": "Without logging and monitoring, breaches cannot be detected"},
    "A10": {"name": "Mishandling of Exceptional Conditions", "description": "Unhandled errors exposing info or enabling denial-of-service"}
}

# Security Scanner Class
class SecurityScanner:
    def __init__(self, target_url: str, scan_id: str):
        self.target_url = target_url
        self.scan_id = scan_id
        self.crawled_urls = set()
        self.vulnerabilities = []
        self.max_pages = 50
        self.timeout = 10
        
    async def crawl(self, url: str, depth: int = 0, max_depth: int = 3):
        """Crawl website and discover URLs"""
        if depth > max_depth or len(self.crawled_urls) >= self.max_pages:
            return
        
        if url in self.crawled_urls:
            return
            
        try:
            parsed = urlparse(url)
            base_domain = parsed.netloc
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                response = await client.get(url)
                self.crawled_urls.add(url)
                
                if 'text/html' not in response.headers.get('content-type', ''):
                    return
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    parsed_full = urlparse(full_url)
                    
                    # Only crawl same domain
                    if parsed_full.netloc == base_domain:
                        await self.crawl(full_url, depth + 1, max_depth)
                        
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
    
    async def check_security_headers(self, url: str) -> List[Vulnerability]:
        """A02: Check for missing security headers"""
        vulns = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                response = await client.get(url)
                headers = response.headers
                
                security_headers = {
                    'Strict-Transport-Security': 'HSTS not configured - enables man-in-the-middle attacks',
                    'X-Content-Type-Options': 'Missing X-Content-Type-Options - enables MIME-type sniffing attacks',
                    'X-Frame-Options': 'Missing X-Frame-Options - enables clickjacking attacks',
                    'Content-Security-Policy': 'Missing CSP - increases XSS attack risk',
                    'X-XSS-Protection': 'Missing X-XSS-Protection header',
                    'Referrer-Policy': 'Missing Referrer-Policy - may leak sensitive URL information'
                }
                
                for header, issue in security_headers.items():
                    if header.lower() not in [h.lower() for h in headers.keys()]:
                        vulns.append(Vulnerability(
                            category=OWASP_CATEGORIES["A02"]["name"],
                            owasp_id="A02",
                            title=f"Missing Security Header: {header}",
                            description=issue,
                            severity="Medium" if header in ['Content-Security-Policy', 'Strict-Transport-Security'] else "Low",
                            url=url,
                            evidence=f"Header '{header}' not found in response",
                            remediation=f"Add the {header} header to your server configuration"
                        ))
                        
                # Check for server version disclosure
                if 'server' in [h.lower() for h in headers.keys()]:
                    server = headers.get('server', '')
                    if any(ver in server.lower() for ver in ['apache', 'nginx', 'iis', 'tomcat']):
                        vulns.append(Vulnerability(
                            category=OWASP_CATEGORIES["A02"]["name"],
                            owasp_id="A02",
                            title="Server Version Disclosure",
                            description="Server version information is exposed in response headers",
                            severity="Low",
                            url=url,
                            evidence=f"Server header: {server}",
                            remediation="Configure server to hide version information"
                        ))
                        
        except Exception as e:
            logger.error(f"Error checking headers for {url}: {e}")
        return vulns
    
    async def check_ssl_tls(self, url: str) -> List[Vulnerability]:
        """A04: Check for cryptographic issues"""
        vulns = []
        parsed = urlparse(url)
        
        if parsed.scheme != 'https':
            vulns.append(Vulnerability(
                category=OWASP_CATEGORIES["A04"]["name"],
                owasp_id="A04",
                title="No HTTPS Encryption",
                description="The website is not using HTTPS encryption",
                severity="High",
                url=url,
                evidence=f"URL scheme is {parsed.scheme}",
                remediation="Implement HTTPS with a valid SSL/TLS certificate"
            ))
        
        return vulns
    
    async def check_injection_points(self, url: str, html_content: str) -> List[Vulnerability]:
        """A05: Check for potential injection vulnerabilities"""
        vulns = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find forms
        forms = soup.find_all('form')
        for form in forms:
            action = form.get('action', '')
            method = form.get('method', 'get').lower()
            
            # Check for forms without CSRF protection
            csrf_fields = form.find_all('input', {'name': re.compile(r'csrf|token|_token', re.I)})
            if not csrf_fields:
                vulns.append(Vulnerability(
                    category=OWASP_CATEGORIES["A01"]["name"],
                    owasp_id="A01",
                    title="Missing CSRF Protection",
                    description="Form is missing CSRF token protection",
                    severity="High",
                    url=url,
                    evidence=f"Form action: {action}, Method: {method}",
                    remediation="Implement CSRF tokens in all forms"
                ))
            
            # Check for potential SQL injection points
            inputs = form.find_all('input')
            for inp in inputs:
                input_name = inp.get('name', '')
                if any(kw in input_name.lower() for kw in ['id', 'user', 'search', 'query', 'filter']):
                    vulns.append(Vulnerability(
                        category=OWASP_CATEGORIES["A05"]["name"],
                        owasp_id="A05",
                        title="Potential SQL Injection Point",
                        description=f"Input field '{input_name}' may be vulnerable to SQL injection",
                        severity="High",
                        url=url,
                        evidence=f"Input name: {input_name}",
                        remediation="Use parameterized queries and input validation"
                    ))
                    break
        
        return vulns
    
    async def check_authentication(self, url: str, html_content: str) -> List[Vulnerability]:
        """A07: Check for authentication issues"""
        vulns = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for password fields without autocomplete off
        password_fields = soup.find_all('input', {'type': 'password'})
        for field in password_fields:
            if field.get('autocomplete') not in ['off', 'new-password', 'current-password']:
                vulns.append(Vulnerability(
                    category=OWASP_CATEGORIES["A07"]["name"],
                    owasp_id="A07",
                    title="Password Field Autocomplete Enabled",
                    description="Password field allows browser autocomplete which may pose security risks",
                    severity="Low",
                    url=url,
                    evidence=f"Password field: {field.get('name', 'unknown')}",
                    remediation="Add autocomplete='off' or 'new-password' to password fields"
                ))
        
        # Check for login forms over HTTP
        login_forms = soup.find_all('form')
        for form in login_forms:
            if any(soup.find_all('input', {'type': 'password'})):
                action = form.get('action', '')
                if action.startswith('http://'):
                    vulns.append(Vulnerability(
                        category=OWASP_CATEGORIES["A07"]["name"],
                        owasp_id="A07",
                        title="Login Form Over HTTP",
                        description="Login form submits credentials over unencrypted HTTP",
                        severity="Critical",
                        url=url,
                        evidence=f"Form action: {action}",
                        remediation="Use HTTPS for all authentication endpoints"
                    ))
        
        return vulns
    
    async def check_information_disclosure(self, url: str, html_content: str) -> List[Vulnerability]:
        """Check for information disclosure issues"""
        vulns = []
        
        # Check for sensitive comments in HTML
        comments = re.findall(r'<!--[\s\S]*?-->', html_content)
        sensitive_patterns = ['password', 'api_key', 'secret', 'todo', 'fixme', 'debug', 'admin']
        for comment in comments:
            if any(pattern in comment.lower() for pattern in sensitive_patterns):
                vulns.append(Vulnerability(
                    category=OWASP_CATEGORIES["A09"]["name"],
                    owasp_id="A09",
                    title="Sensitive Information in HTML Comments",
                    description="HTML comments contain potentially sensitive information",
                    severity="Medium",
                    url=url,
                    evidence=f"Comment found: {comment[:100]}...",
                    remediation="Remove sensitive information from HTML comments before deployment"
                ))
                break
        
        # Check for error messages in content
        error_patterns = [
            r'SQLException', r'ORA-\d+', r'mysql_', r'pg_query',
            r'Warning:', r'Fatal error:', r'Parse error:',
            r'Stack trace:', r'Exception in thread'
        ]
        for pattern in error_patterns:
            if re.search(pattern, html_content, re.I):
                vulns.append(Vulnerability(
                    category=OWASP_CATEGORIES["A10"]["name"],
                    owasp_id="A10",
                    title="Error Message Disclosure",
                    description="Application exposes detailed error messages",
                    severity="Medium",
                    url=url,
                    evidence=f"Error pattern found: {pattern}",
                    remediation="Implement proper error handling and hide detailed error messages"
                ))
                break
        
        return vulns
    
    async def check_insecure_resources(self, url: str, html_content: str) -> List[Vulnerability]:
        """A08: Check for integrity issues with external resources"""
        vulns = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Check for scripts without integrity
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '')
            if src.startswith('http') and 'cdn' in src.lower():
                if not script.get('integrity'):
                    vulns.append(Vulnerability(
                        category=OWASP_CATEGORIES["A08"]["name"],
                        owasp_id="A08",
                        title="External Script Without Integrity Check",
                        description="External script loaded without Subresource Integrity (SRI)",
                        severity="Medium",
                        url=url,
                        evidence=f"Script: {src}",
                        remediation="Add integrity attribute with hash to external scripts"
                    ))
                    break
        
        # Check for mixed content
        if urlparse(url).scheme == 'https':
            insecure_resources = soup.find_all(src=re.compile(r'^http://'))
            insecure_resources.extend(soup.find_all(href=re.compile(r'^http://')))
            if insecure_resources:
                vulns.append(Vulnerability(
                    category=OWASP_CATEGORIES["A08"]["name"],
                    owasp_id="A08",
                    title="Mixed Content",
                    description="HTTPS page loads resources over HTTP",
                    severity="Medium",
                    url=url,
                    evidence="HTTP resources found on HTTPS page",
                    remediation="Ensure all resources are loaded over HTTPS"
                ))
        
        return vulns
    
    async def check_access_control(self, url: str) -> List[Vulnerability]:
        """A01: Check for access control issues"""
        vulns = []
        
        # Check for common admin paths
        admin_paths = ['/admin', '/administrator', '/wp-admin', '/phpmyadmin', '/cpanel', '/.git', '/.env', '/backup']
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False, verify=False) as client:
            for path in admin_paths:
                try:
                    test_url = urljoin(url, path)
                    response = await client.get(test_url)
                    
                    if response.status_code == 200:
                        vulns.append(Vulnerability(
                            category=OWASP_CATEGORIES["A01"]["name"],
                            owasp_id="A01",
                            title=f"Exposed Sensitive Path: {path}",
                            description=f"Sensitive path {path} is accessible without authentication",
                            severity="Critical" if path in ['/.git', '/.env', '/backup'] else "High",
                            url=test_url,
                            evidence=f"HTTP {response.status_code} response",
                            remediation="Restrict access to sensitive paths or remove them from production"
                        ))
                    elif response.status_code in [401, 403]:
                        vulns.append(Vulnerability(
                            category=OWASP_CATEGORIES["A01"]["name"],
                            owasp_id="A01",
                            title=f"Admin Path Discovered: {path}",
                            description=f"Administrative path {path} exists (protected)",
                            severity="Info",
                            url=test_url,
                            evidence=f"HTTP {response.status_code} response",
                            remediation="Ensure strong authentication is required"
                        ))
                except:
                    pass
        
        return vulns
    
    async def check_cors(self, url: str) -> List[Vulnerability]:
        """Check CORS configuration"""
        vulns = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                # Send request with Origin header
                response = await client.get(url, headers={'Origin': 'https://evil.com'})
                
                acao = response.headers.get('Access-Control-Allow-Origin', '')
                acac = response.headers.get('Access-Control-Allow-Credentials', '')
                
                if acao == '*':
                    vulns.append(Vulnerability(
                        category=OWASP_CATEGORIES["A02"]["name"],
                        owasp_id="A02",
                        title="Overly Permissive CORS Policy",
                        description="CORS allows all origins (*)",
                        severity="Medium",
                        url=url,
                        evidence=f"Access-Control-Allow-Origin: {acao}",
                        remediation="Configure CORS to only allow trusted origins"
                    ))
                elif acao == 'https://evil.com' and acac.lower() == 'true':
                    vulns.append(Vulnerability(
                        category=OWASP_CATEGORIES["A02"]["name"],
                        owasp_id="A02",
                        title="CORS Origin Reflection with Credentials",
                        description="CORS reflects origin and allows credentials",
                        severity="High",
                        url=url,
                        evidence=f"Origin reflected: {acao}, Credentials: {acac}",
                        remediation="Do not reflect arbitrary origins with credentials enabled"
                    ))
        except:
            pass
        
        return vulns
    
    async def scan_url(self, url: str) -> List[Vulnerability]:
        """Perform all security checks on a URL"""
        all_vulns = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                response = await client.get(url)
                html_content = response.text
                
                # Run all checks
                all_vulns.extend(await self.check_security_headers(url))
                all_vulns.extend(await self.check_ssl_tls(url))
                all_vulns.extend(await self.check_injection_points(url, html_content))
                all_vulns.extend(await self.check_authentication(url, html_content))
                all_vulns.extend(await self.check_information_disclosure(url, html_content))
                all_vulns.extend(await self.check_insecure_resources(url, html_content))
                all_vulns.extend(await self.check_access_control(url))
                all_vulns.extend(await self.check_cors(url))
                
        except Exception as e:
            logger.error(f"Error scanning {url}: {e}")
        
        return all_vulns
    
    async def run_scan(self):
        """Main scan execution"""
        try:
            # Phase 1: Crawl
            await manager.send_update(self.scan_id, {"status": "crawling", "progress": 10})
            await self.crawl(self.target_url)
            
            # Phase 2: Scan each URL
            total_urls = len(self.crawled_urls)
            for i, url in enumerate(self.crawled_urls):
                progress = 20 + int((i / total_urls) * 60)
                await manager.send_update(self.scan_id, {
                    "status": "scanning",
                    "progress": progress,
                    "current_url": url,
                    "pages_crawled": len(self.crawled_urls)
                })
                
                vulns = await self.scan_url(url)
                self.vulnerabilities.extend(vulns)
            
            # Remove duplicates
            seen = set()
            unique_vulns = []
            for v in self.vulnerabilities:
                key = (v.title, v.url)
                if key not in seen:
                    seen.add(key)
                    unique_vulns.append(v)
            self.vulnerabilities = unique_vulns
            
            return self.vulnerabilities
            
        except Exception as e:
            logger.error(f"Scan error: {e}")
            raise

# AI Analysis
async def get_ai_analysis(vulnerabilities: List[Vulnerability], timeout_seconds: int = 30) -> tuple:
    """Get AI-powered analysis and remediation suggestions with timeout"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key or not vulnerabilities:
            return None, {}
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"scan-{uuid.uuid4()}",
            system_message="""You are an expert cybersecurity analyst. Provide brief, actionable security analysis. Keep responses under 500 words."""
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        vuln_summary = "\n".join([
            f"- {v.severity}: {v.title} ({v.owasp_id})"
            for v in vulnerabilities[:10]
        ])
        
        user_message = UserMessage(
            text=f"""Briefly analyze these vulnerabilities:

{vuln_summary}

Provide: 1) Executive Summary (2 sentences) 2) Top 3 priorities 3) Key remediation steps"""
        )
        
        # Use asyncio.wait_for for timeout
        try:
            response = await asyncio.wait_for(
                chat.send_message(user_message),
                timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.warning("AI analysis timed out")
            return "AI analysis timed out. Please review vulnerabilities manually.", {}
        
        return response, {}
        
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return None, {}

# PDF Report Generation
def generate_pdf_report(scan: dict, output_path: str):
    """Generate a detailed PDF report"""
    doc = SimpleDocTemplate(output_path, pagesize=A4, 
                           rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#00FF94')
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#6E44FF')
    ))
    styles.add(ParagraphStyle(
        name='VulnCritical',
        parent=styles['Normal'],
        textColor=colors.red,
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='VulnHigh',
        parent=styles['Normal'],
        textColor=colors.orange,
        fontName='Helvetica-Bold'
    ))
    
    story = []
    
    # Title
    story.append(Paragraph("KiKi Pentester - Security Report", styles['CustomTitle']))
    story.append(Spacer(1, 12))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['SectionHeader']))
    summary_data = [
        ["Target URL:", scan['target_url']],
        ["Scan Date:", scan['started_at']],
        ["Status:", scan['status']],
        ["Pages Analyzed:", str(scan['pages_crawled'])],
        ["Vulnerabilities Found:", str(scan['vulnerabilities_found'])]
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # AI Summary if available
    if scan.get('ai_summary'):
        story.append(Paragraph("AI Security Analysis", styles['SectionHeader']))
        story.append(Paragraph(scan['ai_summary'], styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Vulnerability Summary by Severity
    story.append(Paragraph("Vulnerability Summary by Severity", styles['SectionHeader']))
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
    for vuln in scan.get('vulnerabilities', []):
        severity = vuln.get('severity', 'Info')
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    severity_data = [["Severity", "Count"]]
    for sev, count in severity_counts.items():
        severity_data.append([sev, str(count)])
    
    severity_table = Table(severity_data, colWidths=[2*inch, 2*inch])
    severity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(severity_table)
    story.append(Spacer(1, 20))
    
    # OWASP Coverage
    story.append(Paragraph("OWASP Top 10 2025 Coverage", styles['SectionHeader']))
    owasp_counts = {k: 0 for k in OWASP_CATEGORIES.keys()}
    for vuln in scan.get('vulnerabilities', []):
        owasp_id = vuln.get('owasp_id', '')
        if owasp_id in owasp_counts:
            owasp_counts[owasp_id] += 1
    
    owasp_data = [["OWASP ID", "Category", "Findings"]]
    for owasp_id, info in OWASP_CATEGORIES.items():
        owasp_data.append([owasp_id, info['name'], str(owasp_counts.get(owasp_id, 0))])
    
    owasp_table = Table(owasp_data, colWidths=[1*inch, 3.5*inch, 1*inch])
    owasp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(owasp_table)
    story.append(PageBreak())
    
    # Detailed Findings
    story.append(Paragraph("Detailed Vulnerability Findings", styles['CustomTitle']))
    
    # Sort by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
    sorted_vulns = sorted(scan.get('vulnerabilities', []), 
                         key=lambda x: severity_order.get(x.get('severity', 'Info'), 5))
    
    for i, vuln in enumerate(sorted_vulns, 1):
        severity = vuln.get('severity', 'Info')
        severity_style = 'VulnCritical' if severity == 'Critical' else ('VulnHigh' if severity == 'High' else 'Normal')
        
        story.append(Paragraph(f"{i}. [{severity}] {vuln.get('title', 'Unknown')}", styles[severity_style]))
        story.append(Spacer(1, 6))
        
        vuln_info = f"""
        <b>OWASP Category:</b> {vuln.get('owasp_id', '')} - {vuln.get('category', '')}<br/>
        <b>URL:</b> {vuln.get('url', '')}<br/>
        <b>Description:</b> {vuln.get('description', '')}<br/>
        """
        if vuln.get('evidence'):
            vuln_info += f"<b>Evidence:</b> {vuln.get('evidence', '')}<br/>"
        if vuln.get('remediation'):
            vuln_info += f"<b>Remediation:</b> {vuln.get('remediation', '')}<br/>"
        if vuln.get('ai_analysis'):
            vuln_info += f"<b>AI Analysis:</b> {vuln.get('ai_analysis', '')}<br/>"
        
        story.append(Paragraph(vuln_info, styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(story)
    return output_path

# Background scan task
async def run_scan_task(scan_id: str, target_url: str):
    """Background task to run the security scan"""
    try:
        # Update status
        await db.scans.update_one(
            {"id": scan_id},
            {"$set": {"status": "crawling", "progress": 5}}
        )
        
        # Run scanner
        scanner = SecurityScanner(target_url, scan_id)
        vulnerabilities = await scanner.run_scan()
        
        # Update with scan results immediately
        vuln_dicts = [v.model_dump() for v in vulnerabilities]
        await db.scans.update_one(
            {"id": scan_id},
            {"$set": {
                "status": "generating_report",
                "progress": 90,
                "pages_crawled": len(scanner.crawled_urls),
                "crawled_urls": list(scanner.crawled_urls),
                "vulnerabilities": vuln_dicts,
                "vulnerabilities_found": len(vulnerabilities)
            }}
        )
        
        await manager.send_update(scan_id, {"status": "generating_report", "progress": 90})
        
        # Generate PDF report first (without AI)
        reports_dir = ROOT_DIR / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_filename = f"scan_report_{scan_id}.pdf"
        report_path = reports_dir / report_filename
        
        scan_doc = {
            "id": scan_id,
            "target_url": target_url,
            "status": "completed",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "pages_crawled": len(scanner.crawled_urls),
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vuln_dicts,
            "ai_summary": None
        }
        
        generate_pdf_report(scan_doc, str(report_path))
        
        # Try to get AI analysis with timeout (non-blocking for completion)
        ai_summary = None
        try:
            ai_summary, _ = await get_ai_analysis(vulnerabilities, timeout_seconds=25)
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
        
        # Final update
        completed_at = datetime.now(timezone.utc).isoformat()
        await db.scans.update_one(
            {"id": scan_id},
            {"$set": {
                "status": "completed",
                "progress": 100,
                "completed_at": completed_at,
                "ai_summary": ai_summary,
                "report_path": report_filename
            }}
        )
        
        await manager.send_update(scan_id, {
            "status": "completed",
            "progress": 100,
            "vulnerabilities_found": len(vulnerabilities)
        })
        
    except Exception as e:
        logger.error(f"Scan task error: {e}")
        await db.scans.update_one(
            {"id": scan_id},
            {"$set": {"status": "failed", "progress": 0}}
        )
        await manager.send_update(scan_id, {"status": "failed", "error": str(e)})

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "Web Application Penetration Testing API"}

@api_router.post("/scans", response_model=dict)
async def create_scan(scan_input: ScanCreate, background_tasks: BackgroundTasks):
    """Start a new security scan"""
    # Validate URL
    try:
        parsed = urlparse(scan_input.target_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL")
    except:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Create scan record
    scan = Scan(target_url=scan_input.target_url)
    scan_dict = scan.model_dump()
    scan_dict['started_at'] = scan_dict['started_at'].isoformat()
    
    await db.scans.insert_one(scan_dict)
    
    # Start background scan
    background_tasks.add_task(run_scan_task, scan.id, scan_input.target_url)
    
    return {"id": scan.id, "status": "pending", "message": "Scan started"}

@api_router.get("/scans", response_model=List[dict])
async def get_all_scans():
    """Get all scans"""
    scans = await db.scans.find({}, {"_id": 0}).sort("started_at", -1).to_list(100)
    return scans

@api_router.get("/scans/{scan_id}", response_model=dict)
async def get_scan(scan_id: str):
    """Get scan by ID"""
    scan = await db.scans.find_one({"id": scan_id}, {"_id": 0})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@api_router.delete("/scans/{scan_id}")
async def delete_scan(scan_id: str):
    """Delete a scan"""
    result = await db.scans.delete_one({"id": scan_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"message": "Scan deleted"}

@api_router.get("/scans/{scan_id}/report")
async def download_report(scan_id: str):
    """Download PDF report"""
    scan = await db.scans.find_one({"id": scan_id}, {"_id": 0})
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan.get('status') != 'completed':
        raise HTTPException(status_code=400, detail="Scan not completed yet")
    
    report_path = ROOT_DIR / "reports" / scan.get('report_path', '')
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=str(report_path),
        filename=f"pentest_report_{scan_id}.pdf",
        media_type="application/pdf"
    )

@api_router.get("/owasp-categories")
async def get_owasp_categories():
    """Get OWASP Top 10 2025 categories"""
    return OWASP_CATEGORIES

# WebSocket endpoint for real-time updates
@app.websocket("/ws/scan/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: str):
    await manager.connect(websocket, scan_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(scan_id)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
