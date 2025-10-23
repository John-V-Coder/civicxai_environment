"""
API Documentation Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.permissions import AllowAny


class APIDocsView(APIView):
    """
    API Documentation - List of all available endpoints
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return API documentation as HTML"""
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CivicXAI API Documentation</title>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }
                h1 { 
                    color: #2c3e50; 
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 { 
                    color: #34495e; 
                    margin-top: 30px;
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                }
                .endpoint { 
                    background: white; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-left: 4px solid #3498db;
                    border-radius: 3px;
                }
                .method { 
                    font-weight: bold; 
                    color: white; 
                    padding: 3px 8px; 
                    border-radius: 3px;
                    display: inline-block;
                    margin-right: 10px;
                }
                .get { background: #27ae60; }
                .post { background: #2980b9; }
                .put { background: #f39c12; }
                .delete { background: #e74c3c; }
                .path { 
                    font-family: 'Courier New', monospace; 
                    color: #2c3e50;
                    font-size: 14px;
                }
                .description { 
                    color: #7f8c8d; 
                    margin-top: 5px;
                }
                .status { 
                    background: #27ae60; 
                    color: white; 
                    padding: 10px; 
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>CivicXAI API Documentation</h1>
            <div class="status">
                API is operational | Django Backend on Port 8000
            </div>
            
            <h2>Allocation Requests</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/allocation-requests/</span>
                <div class="description">List all allocation requests with pagination</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/allocation-requests/create/</span>
                <div class="description">Create new allocation request</div>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/allocation-requests/stats/</span>
                <div class="description">Get allocation request statistics</div>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/allocation-requests/{id}/</span>
                <div class="description">Get specific allocation request (supports both integer pk and UUID)</div>
            </div>
            
            <div class="endpoint">
                <span class="method put">PUT</span>
                <span class="path">/api/allocation-requests/{id}/</span>
                <div class="description">Update allocation request with AI analysis</div>
            </div>
            
            <div class="endpoint">
                <span class="method delete">DELETE</span>
                <span class="path">/api/allocation-requests/{id}/</span>
                <div class="description">Delete allocation request</div>
            </div>
            
            <h2>Chat & Analysis</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/chat/message/</span>
                <div class="description">Send chat message for AI analysis</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/calculate-priority/</span>
                <div class="description">Calculate priority score using MeTTa engine</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/generate-explanation/</span>
                <div class="description">Generate AI explanation for allocation</div>
            </div>
            
            <h2>Cognitive AI Module</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/cognitive/health/</span>
                <div class="description">Check cognitive system health</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/cognitive/query/hybrid/</span>
                <div class="description">Intelligent query routing (MeTTa/Cognitive/Gateway)</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/cognitive/region/analyze/</span>
                <div class="description">Cognitive analysis of region</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/cognitive/ingest/</span>
                <div class="description">Ingest knowledge from documents</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/cognitive/concept/</span>
                <div class="description">Add concept to knowledge base</div>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/cognitive/concepts/</span>
                <div class="description">Query concepts in knowledge base</div>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/cognitive/stats/</span>
                <div class="description">Get knowledge base statistics</div>
            </div>
            
            <h2>Gateway Integration (uAgents)</h2>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/gateway/allocation/request/</span>
                <div class="description">Send allocation request to uAgents gateway</div>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/gateway/explanation/request/</span>
                <div class="description">Request explanation from uAgents</div>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/gateway/status/{request_id}/</span>
                <div class="description">Check gateway request status</div>
            </div>
            
            <h2>System Health</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/health/</span>
                <div class="description">System health check</div>
            </div>
            
            <h2>External Services</h2>
            
            <div style="background: white; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h3>uAgents Gateway</h3>
                <p>If uAgents gateway is running on port 8080:</p>
                <ul>
                    <li><a href="http://localhost:8080/docs" target="_blank">Gateway API Docs</a> - FastAPI auto-generated docs</li>
                    <li><a href="http://localhost:8080/health" target="_blank">Gateway Health</a></li>
                    <li><a href="http://localhost:8080/metrics" target="_blank">Gateway Metrics</a></li>
                </ul>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #ecf0f1; border-radius: 5px;">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="/admin/">Django Admin</a></li>
                    <li><a href="/api/">API Root</a></li>
                    <li><a href="/api/docs/">This Documentation</a></li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html, content_type='text/html')


class APISchemaView(APIView):
    """
    API Schema - Machine-readable API documentation
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return API schema as JSON"""
        
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "CivicXAI API",
                "version": "1.0.0",
                "description": "Resource allocation and explainable AI system"
            },
            "servers": [
                {"url": "http://localhost:8000", "description": "Development server"},
                {"url": "http://localhost:8080", "description": "uAgents Gateway"}
            ],
            "paths": {
                "/api/allocation-requests/": {
                    "get": {"summary": "List allocation requests"},
                    "post": {"summary": "Create allocation request"}
                },
                "/api/cognitive/health/": {
                    "get": {"summary": "Check cognitive system health"}
                },
                "/api/cognitive/query/hybrid/": {
                    "post": {"summary": "Intelligent query routing"}
                }
            }
        }
        
        return Response(schema, status=status.HTTP_200_OK)
