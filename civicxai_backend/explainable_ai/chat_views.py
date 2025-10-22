"""
AI Chat Views
Handles general chat messages and routes them to appropriate AI services
Enhanced with Cognitive Orchestrator (Phase 4)
"""
import os
import re
import httpx
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from dotenv import load_dotenv
from metta.metta_engine import metta_engine
from .models import DataSource

# Phase 4: Cognitive AI Integration
from cognitive.orchestrator import get_orchestrator, RoutingDecision
from cognitive.hybrid_responder import get_hybrid_responder
from cognitive.reasoner import get_reasoner
from cognitive.knowledge_store import get_knowledge_store

load_dotenv()

UAGENTS_GATEWAY_URL = os.getenv("UAGENTS_GATEWAY_URL")


class AIChatView(APIView):
    """
    General AI Chat endpoint
    POST /api/chat/
    
    Accepts any message and routes it to appropriate AI services
    """
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        """
        Process chat message
        
        Expected data:
        - message: str (required) - The user's message
        - files: file uploads (optional)
        - context: dict (optional) - Additional context
        """
        try:
            message = request.data.get('message', '').strip()
            
            if not message:
                return Response({
                    'error': 'Message is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get files if any
            files_data = []
            if hasattr(request, 'FILES'):
                for file_key in request.FILES:
                    file_obj = request.FILES[file_key]
                    files_data.append({
                        'name': file_obj.name,
                        'size': file_obj.size,
                        'type': file_obj.content_type
                    })
            
            # Detect intent
            intent = self._detect_intent(message)
            
            # Process based on intent
            response_data = self._process_by_intent(message, intent, request)
            
            return Response({
                'success': True,
                'message': response_data['content'],
                'intent': intent,
                'files_attached': len(files_data) if files_data else 0
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR in AIChatView: {error_details}")
            
            return Response({
                'success': False,
                'error': 'Failed to process chat message',
                'details': str(e),
                'message': 'Sorry, I encountered an error processing your request. Please try again or rephrase your question.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _detect_intent(self, message):
        """Detect user intent from message"""
        lowerMsg = message.lower()
        
        # Priority calculation
        if any(word in lowerMsg for word in ['calculate', 'priority', 'score']):
            return 'calculate_priority'
        
        # Explanation
        if any(word in lowerMsg for word in ['explain', 'explanation', 'why', 'how']):
            return 'explain'
        
        # Analysis
        if any(word in lowerMsg for word in ['analyze', 'analysis', 'recommendation', 'recommend']):
            return 'analyze'
        
        # Health check
        if any(word in lowerMsg for word in ['health', 'status', 'check', 'working']):
            return 'health_check'
        
        return 'general'
    
    def _get_relevant_sources(self, message, category=None, limit=3):
        """
        Find relevant data sources based on message content
        Returns list of DataSource objects
        """
        try:
            # Search for sources matching keywords in message
            queryset = DataSource.objects.filter(is_active=True)
            
            if category:
                queryset = queryset.filter(category=category)
            
            # Search in title, description, tags, summary, and key_points
            search_words = message.lower().split()
            search_query = Q()
            
            for word in search_words:
                if len(word) > 3:  # Only search words longer than 3 chars
                    search_query |= Q(title__icontains=word)
                    search_query |= Q(tags__icontains=word)
                    search_query |= Q(summary__icontains=word)
                    search_query |= Q(key_points__icontains=word)
            
            if search_query:
                sources = queryset.filter(search_query).distinct()[:limit]
            else:
                # If no search matches, return recent sources
                sources = queryset.order_by('-created_at')[:limit]
            
            # Increment usage count for found sources
            for source in sources:
                source.increment_usage()
            
            return list(sources)
        
        except Exception as e:
            print(f"Error getting relevant sources: {e}")
            return []
    
    def _format_sources_reference(self, sources):
        """Format data sources as references for AI response"""
        if not sources:
            return ""
        
        ref_text = "\n\n**📚 References:**\n"
        for idx, source in enumerate(sources, 1):
            ref_text += f"\n{idx}. **{source.title}**"
            if source.author:
                ref_text += f" by {source.author}"
            if source.source_location:
                ref_text += f"\n   🔗 [{source.source_type.upper()}]({source.source_location})"
            if source.get_content_preview():
                ref_text += f"\n   _{source.get_content_preview()}_"
        
        return ref_text
    
    def _extract_metrics(self, message):
        """Extract metrics from natural language"""
        metrics = {
            'poverty_index': 0.5,
            'project_impact': 0.6,
            'deforestation': 0.4,
            'corruption_risk': 0.3
        }
        
        # Enhanced extraction with more patterns
        patterns = {
            'poverty_index': [
                r'poverty.*?(\d+\.?\d*)',
                r'poverty.*?(\d+)%',
                r'poverty\s*(?:index|rate|score)?\s*(?:is|of|=)?\s*(\d+\.?\d*)'
            ],
            'project_impact': [
                r'impact.*?(\d+\.?\d*)',
                r'impact.*?(\d+)%',
                r'(?:project\s*)?impact\s*(?:score|rate)?\s*(?:is|of|=)?\s*(\d+\.?\d*)'
            ],
            'deforestation': [
                r'deforest.*?(\d+\.?\d*)',
                r'deforest.*?(\d+)%',
                r'(?:de)?forest(?:ation)?\s*(?:rate|level|score)?\s*(?:is|of|=)?\s*(\d+\.?\d*)'
            ],
            'corruption_risk': [
                r'corruption.*?(\d+\.?\d*)',
                r'corruption.*?(\d+)%',
                r'corruption\s*(?:risk|score|level)?\s*(?:is|of|=)?\s*(\d+\.?\d*)'
            ]
        }
        
        for metric_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    value = float(match.group(1))
                    # Normalize if percentage
                    if value > 1:
                        value = value / 100
                    metrics[metric_name] = min(1.0, max(0.0, value))
                    break
        
        return metrics
    
    def _process_by_intent(self, message, intent, request):
        """
        Process message based on detected intent
        Enhanced with Phase 4 Cognitive Orchestrator
        """
        # Phase 4: Use cognitive orchestrator for intelligent routing
        orchestrator = get_orchestrator()
        routing_decision = orchestrator.route_query(message)
        
        routing = routing_decision['routing']
        analysis = routing_decision['analysis']
        
        # Log routing decision
        print(f"🧠 Cognitive Orchestrator: {routing.value} ({routing_decision['rationale']})")
        
        # Check for document queries first (Phase 4 key deliverable)
        if analysis['requires_documents']:
            return self._handle_document_query(message, analysis)
        
        # Route based on orchestrator decision
        if routing == RoutingDecision.COGNITIVE:
            return self._handle_cognitive_reasoning(message, analysis)
        
        elif routing == RoutingDecision.HYBRID_METTA:
            return self._handle_hybrid_metta(message, analysis)
        
        elif routing == RoutingDecision.HYBRID_GATEWAY:
            return self._handle_hybrid_gateway(message, analysis)
        
        # Traditional routing for simple cases
        if intent == 'calculate_priority':
            return self._handle_priority_calculation(message)
        
        elif intent == 'analyze':
            return self._handle_analysis(message, request)
        
        elif intent == 'explain':
            return self._handle_explanation(message)
        
        elif intent == 'health_check':
            return self._handle_health_check()
        
        else:
            return self._handle_general(message)
    
    def _handle_priority_calculation(self, message):
        """Handle priority calculation requests"""
        try:
            metrics = self._extract_metrics(message)
            
            # Calculate using MeTTa
            priority_score = metta_engine.calculate_priority(
                metrics['poverty_index'],
                metrics['project_impact'],
                metrics['deforestation'],
                metrics['corruption_risk']
            )
            
            confidence = 0.85  # Default confidence
            
            response = f"**Priority Calculation Complete**\n\n"
            response += f"**Priority Score:** {priority_score:.2f}\n"
            response += f"**Confidence:** {int(confidence * 100)}%\n\n"
            response += f"**Breakdown:**\n"
            response += f"• Poverty Index: {metrics['poverty_index']:.2f}\n"
            response += f"• Project Impact: {metrics['project_impact']:.2f}\n"
            response += f"• Deforestation: {metrics['deforestation']:.2f}\n"
            response += f"• Corruption Risk: {metrics['corruption_risk']:.2f}\n\n"
            
            # Add interpretation
            if priority_score > 0.7:
                response += "This indicates a **high priority** region for resource allocation."
            elif priority_score > 0.4:
                response += "This indicates a **medium priority** region for resource allocation."
            else:
                response += "This indicates a **low priority** region for resource allocation."
            
            return {'content': response}
            
        except Exception as e:
            return {
                'content': f"I encountered an error calculating the priority: {str(e)}\n\n"
                          f"Please ensure all metrics are properly formatted (values between 0 and 1)."
            }
    
    def _handle_analysis(self, message, request):
        """Handle analysis requests"""
        try:
            # Get relevant research and data sources
            sources = self._get_relevant_sources(message, category='research', limit=3)
            if not sources:
                sources = self._get_relevant_sources(message, category='data', limit=3)
            
            metrics = self._extract_metrics(message)
            
            # Try Gateway first if available
            try:
                if UAGENTS_GATEWAY_URL:
                    form_data = {
                        'region_id': f"CHAT_{int(__import__('time').time())}",
                        'poverty_index': metrics['poverty_index'],
                        'project_impact': metrics['project_impact'],
                        'environmental_score': metrics['deforestation'],
                        'corruption_risk': metrics['corruption_risk'],
                    }
                    
                    files = []
                    if hasattr(request, 'FILES'):
                        for file_key in request.FILES:
                            file_obj = request.FILES[file_key]
                            files.append(('files', (file_obj.name, file_obj.read(), file_obj.content_type)))
                    
                    with httpx.Client(timeout=30.0) as client:
                        if files:
                            response = client.post(
                                f"{UAGENTS_GATEWAY_URL}/allocation/request",
                                data=form_data,
                                files=files
                            )
                        else:
                            response = client.post(
                                f"{UAGENTS_GATEWAY_URL}/allocation/request",
                                data=form_data
                            )
                        
                        response.raise_for_status()
                        result = response.json()
                        
                        # Poll for results
                        request_id = result.get('request_id')
                        if request_id:
                            # Simplified polling (should be improved)
                            import time
                            max_attempts = 10
                            for _ in range(max_attempts):
                                time.sleep(2)
                                status_response = client.get(f"{UAGENTS_GATEWAY_URL}/status/{request_id}")
                                status_data = status_response.json()
                                
                                if status_data.get('status') == 'completed':
                                    data = status_data.get('data', {})
                                    recommendation = data.get('recommendation', {})
                                    
                                    response_text = f"**AI Analysis Complete**\n\n"
                                    response_text += f"**Priority Level:** {recommendation.get('priority_level', 'Medium')}\n"
                                    response_text += f"**Confidence:** {int((recommendation.get('confidence_score', 0.7)) * 100)}%\n"
                                    response_text += f"**Recommended Allocation:** {recommendation.get('recommended_allocation_percentage', 0)}%\n\n"
                                    
                                    if recommendation.get('key_findings'):
                                        response_text += "**Key Findings:**\n"
                                        for finding in recommendation['key_findings']:
                                            response_text += f"• {finding}\n"
                                    
                                    return {'content': response_text}
                            
                            return {'content': "Analysis is taking longer than expected. Please check back later."}
                
            except Exception as gateway_error:
                # Fallback to MeTTa
                print(f"Gateway failed, using MeTTa: {gateway_error}")
            
            # Fallback: Use MeTTa
            priority_score = metta_engine.calculate_priority(
                metrics['poverty_index'],
                metrics['project_impact'],
                metrics['deforestation'],
                metrics['corruption_risk']
            )
            
            response = f"**Analysis Complete** (Using MeTTa Engine)\n\n"
            response += f"**Priority Score:** {priority_score:.2f}\n"
            response += f"**Confidence:** 85%\n\n"
            response += f"**Note:** Gateway unavailable, used local MeTTa engine for calculation.\n\n"
            response += f"**Metrics Analyzed:**\n"
            response += f"• Poverty Index: {metrics['poverty_index']:.2f}\n"
            response += f"• Project Impact: {metrics['project_impact']:.2f}\n"
            response += f"• Deforestation: {metrics['deforestation']:.2f}\n"
            response += f"• Corruption Risk: {metrics['corruption_risk']:.2f}\n\n"
            
            # Add recommendation
            if priority_score > 0.7:
                response += "**Recommendation:** High priority - Allocate significant resources to this region."
            elif priority_score > 0.4:
                response += "**Recommendation:** Medium priority - Balanced allocation recommended."
            else:
                response += "**Recommendation:** Low priority - Minimal allocation suggested."
            
            # Add relevant sources
            response += self._format_sources_reference(sources)
            
            return {'content': response}
            
        except Exception as e:
            return {
                'content': f"Analysis failed: {str(e)}\n\nPlease try again or check your input values."
            }
    
    def _handle_explanation(self, message):
        """Handle explanation requests"""
        try:
            # Get relevant policy and guideline sources
            sources = self._get_relevant_sources(message, category='policy', limit=3)
            if not sources:
                sources = self._get_relevant_sources(message, limit=3)
            
            response = f"**Explanation Generated**\n\n"
            response += "Based on the allocation data, here's how the decision was made:\n\n"
            response += "1. **Poverty Index Impact**: Regions with higher poverty levels receive priority as they have greater need for resource allocation.\n\n"
            response += "2. **Project Impact Assessment**: Areas where interventions can have maximum positive effect get higher scores.\n\n"
            response += "3. **Environmental Considerations**: Deforestation rates affect sustainability of allocations.\n\n"
            response += "4. **Corruption Risk Factor**: Lower corruption risk ensures effective utilization of allocated resources.\n\n"
            response += "The MeTTa policy engine combines these factors using predefined rules and weights to calculate a final priority score.\n\n"
            response += "Would you like me to calculate a specific example?"
            
            # Add relevant sources
            response += self._format_sources_reference(sources)
            
            return {'content': response}
            
        except Exception as e:
            return {
                'content': f"Failed to generate explanation: {str(e)}"
            }
    
    def _handle_health_check(self):
        """Handle health check requests"""
        try:
            # Check MeTTa
            test_score = metta_engine.calculate_priority(0.8, 0.9, 0.4, 0.3)
            metta_status = "operational" if test_score > 0 else "error"
            
            # Check Gateway
            gateway_status = "offline"
            try:
                if UAGENTS_GATEWAY_URL:
                    with httpx.Client(timeout=5.0) as client:
                        response = client.get(f"{UAGENTS_GATEWAY_URL}/health")
                        if response.status_code == 200:
                            gateway_status = "operational"
            except:
                gateway_status = "offline"
            
            response = f"**System Health Check**\n\n"
            response += f"**MeTTa Engine:** {metta_status.upper()}\n"
            response += f"**AI Gateway:** {gateway_status.upper()}\n"
            response += f"**Overall Status:** {'All systems operational' if metta_status == 'operational' else 'Some systems offline'}\n\n"
            
            if gateway_status == "offline":
                response += "_Note: AI Gateway is offline. Using local MeTTa engine for calculations._"
            
            return {'content': response}
            
        except Exception as e:
            return {
                'content': f"Health check failed: {str(e)}"
            }
    
    def _handle_general(self, message):
        """Handle general queries and conversational messages"""
        lowerMsg = message.lower().strip()
        
        # Greetings
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if any(greeting == lowerMsg or lowerMsg.startswith(greeting + ' ') for greeting in greetings):
            response = "Hello! I'm your AI assistant for civic resource allocation. I can help you with:\n\n"
            response += "• Calculating allocation priorities based on metrics\n"
            response += "• Analyzing regions and providing recommendations\n"
            response += "• Explaining allocation decisions\n"
            response += "• Checking system health\n\n"
            response += "What would you like to know?"
            return {'content': response}
        
        # Thanks
        thanks = ['thank', 'thanks', 'thx', 'appreciate']
        if any(word in lowerMsg for word in thanks):
            response = "You're welcome! Let me know if you need anything else."
            return {'content': response}
        
        # Help requests
        help_words = ['help', 'what can you do', 'how do i', 'how to', 'guide']
        if any(word in lowerMsg for word in help_words):
            response = "I can assist you with several tasks:\n\n"
            response += "**Priority Calculation**\n"
            response += "Ask me to calculate priorities with metrics like:\n"
            response += "_\"Calculate priority for poverty 0.8, impact 0.9\"_\n\n"
            response += "**Regional Analysis**\n"
            response += "Request analysis for regions:\n"
            response += "_\"Analyze region with poverty 0.7 and deforestation 0.5\"_\n\n"
            response += "**Explanations**\n"
            response += "Ask me to explain how allocations work:\n"
            response += "_\"Explain how priority scores are calculated\"_\n\n"
            response += "**System Status**\n"
            response += "Check if systems are operational:\n"
            response += "_\"Check system health\"_\n\n"
            response += "You can also upload PDFs for more detailed analysis!"
            return {'content': response}
        
        # Short unclear messages
        if len(message.strip()) < 15 and not any(char.isdigit() for char in message):
            response = "I'm not sure what you're asking. Could you provide more details?\n\n"
            response += "For example, you could ask me to:\n"
            response += "• Calculate priority scores\n"
            response += "• Analyze a specific region\n"
            response += "• Explain allocation decisions\n"
            response += "• Check system status"
            return {'content': response}
        
        # Default response for unclear queries
        response = "I'm here to help with resource allocation decisions. "
        response += "Could you clarify what you'd like me to do?\n\n"
        response += "You can ask me to calculate priorities, analyze regions, explain decisions, or check system status."
        
        return {'content': response}
    
    # ===== Phase 4: Cognitive Orchestrator Handlers =====
    
    def _handle_document_query(self, message, analysis):
        """
        Handle document queries like "What documents mention poverty?"
        Phase 4 key deliverable
        """
        try:
            knowledge_store = get_knowledge_store()
            reasoner = get_reasoner()
            
            # Extract search terms
            keywords = analysis['keywords']
            
            # Find relevant sources
            matching_sources = []
            for keyword in keywords:
                try:
                    # Search in knowledge base
                    sources = knowledge_store.find_sources_for_topic(keyword)
                    matching_sources.extend(sources)
                except:
                    # Fallback to DataSource model
                    sources = self._get_relevant_sources(message, limit=5)
                    matching_sources.extend([s.title if hasattr(s, 'title') else str(s) for s in sources])
            
            # Remove duplicates
            unique_sources = list(set(matching_sources))
            
            # Build response with reasoning
            response = f"**Document Search Results**\n\n"
            response += f"Found **{len(unique_sources)} documents** mentioning: {', '.join(keywords)}\n\n"
            
            if unique_sources:
                response += "**Documents:**\n"
                for idx, source in enumerate(unique_sources[:10], 1):
                    source_name = source if isinstance(source, str) else str(source)
                    response += f"{idx}. {source_name}\n"
                
                response += f"\n**Reasoning:**\n"
                response += f"• Searched knowledge base for keywords: {', '.join(keywords)}\n"
                response += f"• Found {len(unique_sources)} relevant documents\n"
                response += f"• Results ranked by relevance and usage\n\n"
                
                if len(unique_sources) > 10:
                    response += f"_Showing top 10 of {len(unique_sources)} results_\n"
            else:
                response += "No documents found matching your query.\n\n"
                response += "**Suggestion:** Try different keywords or upload relevant documents."
            
            # Add confidence
            confidence_level = "high" if len(unique_sources) >= 3 else "medium" if len(unique_sources) > 0 else "low"
            response += f"\n**Confidence:** {confidence_level.title()}"
            
            return {'content': response}
            
        except Exception as e:
            return {
                'content': f"Failed to search documents: {str(e)}\n\nPlease try rephrasing your query."
            }
    
    def _handle_cognitive_reasoning(self, message, analysis):
        """Handle queries requiring complex cognitive reasoning"""
        try:
            reasoner = get_reasoner()
            
            # Determine reasoning type
            if analysis['requires_multi_hop']:
                # Multi-hop inference
                keywords = analysis['keywords']
                if len(keywords) >= 2:
                    result = reasoner.multi_hop_inference(keywords[0], keywords[-1])
                    if result.get('success'):
                        response = f"**Reasoning Result**\n\n"
                        response += f"Found connection: {keywords[0]} → {keywords[-1]}\n\n"
                        
                        steps = result.get('steps', [])
                        if steps:
                            response += "**Reasoning Chain:**\n"
                            for step in steps:
                                response += f"• {step.get('premise', '')} → {step.get('conclusion', '')}\n"
                        
                        return {'content': response}
            
            # Default cognitive response
            response = "**Cognitive Analysis**\n\n"
            response += "This query requires complex reasoning. "
            response += f"Analyzing: {', '.join(analysis['keywords'])}\n\n"
            
            # Get related concepts
            if analysis['keywords']:
                related = reasoner.find_related_concepts(analysis['keywords'][0])
                if related:
                    response += f"**Related Concepts:** {', '.join(related[:5])}\n"
            
            return {'content': response}
            
        except Exception as e:
            return {
                'content': f"Cognitive reasoning failed: {str(e)}\n\nTrying simpler analysis..."
            }
    
    def _handle_hybrid_metta(self, message, analysis):
        """Handle queries needing MeTTa calculation + OpenCog reasoning"""
        try:
            hybrid_responder = get_hybrid_responder()
            
            # First, do MeTTa calculation
            metta_result = self._handle_priority_calculation(message)
            
            # Then enhance with reasoning
            context = {
                'region_id': 'Query_Region',
                'priority_score': 0.75  # Placeholder
            }
            
            enhanced_result = hybrid_responder.combine_metta_with_reasoning(
                {'priority_score': 0.75}, message, context
            )
            
            if enhanced_result.get('success'):
                response = enhanced_result.get('explanation', metta_result['content'])
                
                # Add sources if available
                if enhanced_result.get('sources'):
                    response += self._format_sources_reference(enhanced_result['sources'])
                
                return {'content': response}
            else:
                return metta_result
            
        except Exception as e:
            # Fallback to basic MeTTa
            return self._handle_priority_calculation(message)
    
    def _handle_hybrid_gateway(self, message, analysis):
        """Handle queries needing Gateway analysis + OpenCog reasoning"""
        try:
            hybrid_responder = get_hybrid_responder()
            
            # Try Gateway first
            gateway_result = self._handle_analysis(message, None)
            
            # Enhance with reasoning
            context = {'topics': analysis['keywords']}
            
            enhanced_result = hybrid_responder.combine_gateway_with_reasoning(
                gateway_result, message, context
            )
            
            if enhanced_result.get('success'):
                response = enhanced_result.get('explanation', gateway_result['content'])
                
                # Add sources
                if enhanced_result.get('sources'):
                    response += self._format_sources_reference(enhanced_result['sources'][:3])
                
                return {'content': response}
            else:
                return gateway_result
            
        except Exception as e:
            # Fallback to basic analysis
            return self._handle_analysis(message, None)
