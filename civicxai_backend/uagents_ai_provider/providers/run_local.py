#!/usr/bin/env python3
"""
Simplified local runner for CivicXAI Provider Agent
This runs without Almanac registration to avoid testnet fund issues
"""
import os
import sys

# Force disable Almanac before any imports
os.environ["DISABLE_ALMANAC"] = "true"
os.environ["ALMANAC_API_DISABLED"] = "1"
os.environ["NO_ALMANAC_REGISTRATION"] = "true"

# Optional: Set API keys here for testing (remove in production)
# os.environ["OPENAI_API_KEY"] = "your-key-here"
# os.environ["ANTHROPIC_API_KEY"] = "your-key-here"

print("=" * 60)
print("Starting CivicXAI Provider Agent (Local Mode)")
print("=" * 60)
print()
print("Configuration:")
print("  - Almanac: DISABLED ")
print("  - Mode: LOCAL ONLY")
print("  - Port: 8002")
print()

# Import and run main
try:
    from main import main
    import asyncio
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nAgent stopped by user")
except Exception as e:
    print(f" Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
