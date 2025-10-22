# 🚀 Phase 2: Quick Start Guide

## Installation (5 minutes)

```bash
cd civicxai_backend

# Already done in Phase 1, but make sure:
pip install -r requirements.txt

# Download spaCy model (IMPORTANT!)
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy ready')"
```

---

## Test Phase 2 (2 minutes)

```bash
# Run Phase 2 tests
python cognitive/tests/test_ingestion_pipeline.py

# Expected: ✅ 12/12 tests passed
```

---

## Initialize Knowledge Base (1 minute)

```bash
# Start Django server
python manage.py runserver

# In another terminal, initialize domain knowledge
curl -X POST http://localhost:8000/api/cognitive/ingest/initialize/
```

**Response:**
```json
{
  "success": true,
  "message": "Domain knowledge initialized",
  "stats": {
    "concepts": 17,
    "similarities": 10,
    "causal_links": 6
  }
}
```

---

## Upload Your First PDF (30 seconds)

```bash
# Upload a policy document
curl -X POST http://localhost:8000/api/cognitive/ingest/pdf/ \
  -F "file=@your_document.pdf" \
  -F "source_id=MyFirstDoc"
```

**Response:**
```json
{
  "success": true,
  "source_id": "MyFirstDoc",
  "pages": 25,
  "concepts_extracted": 150,
  "atoms_created": 200,
  "key_topics": ["Poverty", "Allocation", "Development"]
}
```

---

## Query the Knowledge (30 seconds)

```bash
# Check knowledge base stats
curl http://localhost:8000/api/cognitive/stats/

# Find concepts
curl http://localhost:8000/api/cognitive/concepts/

# Perform reasoning
curl -X POST http://localhost:8000/api/cognitive/reason/ \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "find_evidence",
    "parameters": {
      "decision": "high_priority",
      "context": {"topics": ["poverty", "allocation"]}
    }
  }'
```

---

## Use in Python (1 minute)

```python
from cognitive.ingestion_pipeline import get_ingestion_pipeline

# Process a PDF
pipeline = get_ingestion_pipeline()
result = pipeline.process_pdf_file('document.pdf', 'Doc_123')

print(f"Success: {result['success']}")
print(f"Atoms created: {result['atoms_created']}")
print(f"Topics: {result['key_topics']}")
```

---

## Auto-Processing (via Django Admin)

1. Go to: `http://localhost:8000/admin`
2. Click "Data sources" → "Add"
3. Upload PDF
4. Save
5. ✅ Automatically processed!

---

## Troubleshooting

### spaCy model not found?
```bash
python -m spacy download en_core_web_sm
```

### Tests failing?
```bash
# Run Phase 1 tests first
python cognitive/tests/test_cognitive_system.py

# Then Phase 2 tests
python cognitive/tests/test_ingestion_pipeline.py
```

### API not working?
```bash
# Check server is running
curl http://localhost:8000/api/cognitive/health/

# Should return: {"status": "healthy"}
```

---

## That's It! 🎉

You now have:
- ✅ Automatic PDF processing
- ✅ NLP concept extraction
- ✅ Knowledge graph generation
- ✅ API for ingestion
- ✅ Auto-processing on upload

**Ready for Phase 3: Advanced Reasoning!**
