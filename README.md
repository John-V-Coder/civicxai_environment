# 🌍 CivicXAI Environment - Explainable AI for Civic Resource Allocation

## 📋 Project Overview

CivicXAI is an **Explainable AI Agent System** designed to provide transparent, accountable, and interpretable decisions for civic resource allocation (e.g., budget distribution, infrastructure funding, environmental projects). The system combines multiple AI technologies to ensure both optimal decision-making and human-understandable explanations.

### 🎯 Core Purpose
- **Transparent Governance**: Make AI-driven civic decisions understandable to citizens
- **Fair Resource Allocation**: Use multi-factor analysis for equitable distribution
- **Policy Compliance**: Ensure decisions align with governance rules
- **Actionable Insights**: Provide clear recommendations for civic improvements

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + Vite)                  │
│                    [Currently: Template Only]                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Django Backend (Port 8000)                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ API Endpoints:                                      │    │
│  │ • /api/calculate-priority/  (MeTTa calculations)    │    │
│  │ • /api/explain/  (ASI:One explanations)            │    │
│  │ • /api/health/  (System health check)              │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ MeTTa Engine (Policy Rules)                        │    │
│  │ • Weighted scoring (poverty, impact, environment)   │    │
│  │ • Corruption penalty calculations                   │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ ASI:One Explain Agent                              │    │
│  │ • Natural language explanations                     │    │
│  │ • Uses ASI:One API for reasoning                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ uAgent Communication
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          uAgents Microservices Architecture                  │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  Gateway Agent       │    │  AI Provider Agent   │      │
│  │  (Port 8000/9000)    │◄───┤  (Port 8002)        │      │
│  │  • FastAPI endpoint  │    │  • OpenAI GPT-4     │      │
│  │  • Request routing   │    │  • Context analysis  │      │
│  └──────────────────────┘    └──────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Components Breakdown

### 1. **Django Backend** (`civicxai_backend/`)
- **Framework**: Django 5.1.6 + Django REST Framework
- **Key Features**:
  - RESTful API endpoints for priority calculations
  - Integration with MeTTa symbolic reasoning engine
  - ASI:One API integration for explanations
  - Currently no database models (uses in-memory calculations)

### 2. **MeTTa Engine** (`civicxai_backend/metta/`)
- **Technology**: [MeTTa Language](https://metta-lang.dev/) - SingularityNET's symbolic AI language for AGI
- **Purpose**: Transparent, rule-based decision making for fund allocation
- **Implementation**: Hyperon framework with Python integration
- **Key Features**:
  - Symbolic reasoning for explainable AI decisions
  - Pattern matching and logical inference
  - Human-readable policy rules
  - No black-box algorithms - fully auditable
- **Weighted Scoring System**:
  - Poverty Index: 40% weight (socioeconomic need)
  - Project Impact: 30% weight (community benefit)
  - Environmental Factors: 20% weight (sustainability)
  - Corruption Risk: -10% penalty (risk mitigation)

### 3. **uAgents Gateway** (`uagents_gateway/`) ✅ **IMPLEMENTED**
- **Framework**: [uAgents](https://docs.agentverse.ai) + FastAPI
- **Purpose**: Decentralized agent communication gateway
- **Features**:
  - RESTful API for client applications
  - Agent-to-agent protocol communication
  - Request tracking and caching
  - Agentverse network integration (optional)
- **Documentation**: See [UAGENTS_DOCUMENTATION.md](./UAGENTS_DOCUMENTATION.md)

### 4. **uAgents AI Provider** (`uagents_ai_provider/`) ✅ **FULLY INTEGRATED**
- **Frameworks**: 
  - [uAgents](https://docs.agentverse.ai) - Decentralized agent protocol
  - [ASI:One](https://docs.asi1.ai) - AI governance standards
  - [CUDOS](https://docs.cudos.org) - Decentralized compute network
- **Purpose**: Multi-source AI processing with decentralized compute
- **Key Features**:
  - **Multiple AI Sources**: OpenAI GPT-4o, ASI:One, MeTTa symbolic reasoning
  - **Decentralized Compute**: CUDOS network for verifiable computation
  - **Multi-language Support**: Explanations in multiple languages
  - **Verification**: Cryptographic hashes for audit trails
  - **Hybrid Processing**: Intelligent routing between local and decentralized
- **Files**:
  - `ai_provider_enhanced.py` - Standard implementation
  - `ai_provider_cudos.py` - Full integration with CUDOS
  - `asi1_governance.py` - ASI:One governance agent
- **Documentation**: See [CUDOS_INTEGRATION.md](./CUDOS_INTEGRATION.md)

### 5. **Frontend** (`civicxai_frontend/`) ✅ **IMPLEMENTED**
- **Framework**: React + Vite + TailwindCSS + shadcn/ui
- **Features**:
  - Beautiful dark theme dashboard
  - Guest mode (no login required)
  - Responsive design
  - Real-time metrics visualization
- **Documentation**: See [UI_SETUP_GUIDE.md](./UI_SETUP_GUIDE.md)

## 🚨 What's Missing / Needs Implementation

### Critical Missing Components:

1. **Frontend Implementation**
   - [ ] Dashboard for resource allocation visualization
   - [ ] Explanation request interface
   - [ ] Real-time allocation tracking
   - [ ] Interactive maps for regional data
   - [ ] Admin panel for policy configuration

2. **Data Integration**
   - [ ] Database models for regions, allocations, metrics
   - [ ] CSV/Excel data import functionality
   - [ ] Historical allocation tracking
   - [ ] Real-time data feeds integration

3. **Machine Learning Models**
   - [ ] Decision tree or random forest for allocation predictions
   - [ ] SHAP/LIME integration for model interpretability
   - [ ] Feature importance calculations
   - [ ] Model training pipeline

4. **Authentication & Security**
   - [ ] User authentication system
   - [ ] Role-based access control
   - [ ] API key management
   - [ ] Request rate limiting

5. **Monitoring & Analytics**
   - [ ] Logging system
   - [ ] Performance metrics
   - [ ] Explanation quality tracking
   - [ ] User feedback collection

## 🚀 Prototype Implementation Plan

### Phase 1: Core Functionality (1-2 days)
```python
# 1. Create Django models
class Region(models.Model):
    name = models.CharField(max_length=100)
    poverty_index = models.FloatField()
    deforestation_rate = models.FloatField()
    population = models.IntegerField()
    
class Allocation(models.Model):
    region = models.ForeignKey(Region)
    amount = models.DecimalField()
    explanation = models.TextField()
    created_at = models.DateTimeField()
```

### Phase 2: Frontend Dashboard (2-3 days)
```jsx
// Main dashboard component
const AllocationDashboard = () => {
  return (
    <div className="grid grid-cols-3 gap-4">
      <RegionSelector />
      <AllocationChart />
      <ExplanationPanel />
    </div>
  );
};
```

### Phase 3: Complete Integration (1-2 days)
- Connect all services
- Test end-to-end flow
- Deploy to staging environment

## 📝 Environment Configuration

### Required API Keys:
```env
# Django Backend (.env)
ASI_ONE_API_KEY=your_asi_one_key
SECRET_KEY=your_django_secret

# uAgents AI Provider (.env)
OPENAI_API_KEY=your_openai_key
AI_PROVIDER_AGENT_SEED=unique_seed

# uAgents Gateway (.env)
GATEWAY_AGENT_SEED=unique_seed
AI_PROVIDER_AGENT_ADDRESS=agent_address_from_provider
```

## 🔄 Current Data Flow

1. **User Request** → Django API (`/api/explain/`)
2. **Django** → Calculates priority using MeTTa rules
3. **Django** → Requests explanation from ASI:One API
4. **Parallel**: uAgent Gateway receives requests
5. **Gateway** → Forwards to AI Provider Agent
6. **AI Provider** → Generates explanation via OpenAI
7. **Response** → Returns to user with explanation + recommendations

## 🛠️ Quick Start Guide

### 1. Backend Setup:
```bash
cd civicxai_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. uAgents Setup:
```bash
# Terminal 1 - AI Provider
cd uagents_ai_provider
python main.py

# Terminal 2 - Gateway
cd uagents_gateway/gateway
python main.py
```

### 3. Frontend (when implemented):
```bash
cd civicxai_frontend
npm install
npm run dev
```

## 📊 Example API Usage

### Calculate Priority:
```json
POST /api/calculate-priority/
{
  "poverty_index": 0.8,
  "project_impact": 0.9,
  "deforestation": 0.4,
  "corruption_risk": 0.3
}
```

### Get Explanation:
```json
POST /api/explain/
{
  "region_id": "kakamega_001",
  "metric_data": {
    "poverty": 0.8,
    "deforestation": 0.75
  },
  "current_allocation": "high",
  "explanation_context": "Why this allocation?"
}
```

## 🎯 Next Steps for Prototype

1. **Immediate Actions**:
   - Implement basic Django models
   - Create sample dataset
   - Build minimal frontend dashboard

2. **Testing**:
   - Unit tests for MeTTa calculations
   - API endpoint tests
   - uAgent communication tests

3. **Documentation**:
   - API documentation (Swagger/OpenAPI)
   - User guide
   - Deployment instructions

## 🏆 Success Metrics

- **Explanation Clarity**: 90%+ user understanding rate
- **Decision Accuracy**: Aligned with policy rules
- **Response Time**: <2 seconds for explanations
- **System Uptime**: 99.9% availability

## 🤝 Contributing

This is a prototype for demonstrating explainable AI in civic governance. To contribute:
1. Focus on completing missing components
2. Ensure all AI decisions are traceable
3. Maintain transparency in algorithms
4. Document all policy rules

## 📄 License

[Specify your license here]

---

**Note**: This is a work-in-progress prototype. The system demonstrates the potential of explainable AI in civic governance but requires completion of the frontend and data integration components for full functionality.
