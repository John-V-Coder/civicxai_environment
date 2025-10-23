#!/usr/bin/env python
"""
Quick setup and run script for CivicXAI uAgents
Based on:
- https://docs.agentverse.ai/home
- https://docs.asi1.ai/documentation/getting-started/overview
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_requirements():
    """Check if required packages are installed"""
    print_header("Checking Requirements")
    
    required = {
        "uagents": "pip install uagents",
        "fastapi": "pip install fastapi",
        "openai": "pip install openai",
        "dotenv": "pip install python-dotenv"
    }
    
    missing = []
    for package, install_cmd in required.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✓ {package} installed")
        except ImportError:
            print(f"  ✗ {package} missing")
            missing.append(install_cmd)
    
    if missing:
        print("\n[ERROR] Missing packages. Install with:")
        for cmd in missing:
            print(f"  {cmd}")
        return False
    
    print("\n All requirements satisfied!")
    return True

def check_env_files():
    """Check if .env files are configured"""
    print_header("Checking Configuration")
    
    base_dir = Path(__file__).parent
    
    # Check gateway .env
    gateway_env = base_dir / "uagents_gateway" / ".env"
    if not gateway_env.exists():
        print(f"  ✗ Gateway .env missing at {gateway_env}")
        create_default_env(gateway_env, "gateway")
    else:
        print(f"  ✓ Gateway .env found")
    
    # Check AI provider .env
    provider_env = base_dir / "uagents_ai_provider" / ".env"
    if not provider_env.exists():
        print(f"  ✗ AI Provider .env missing at {provider_env}")
        create_default_env(provider_env, "provider")
    else:
        print(f"  ✓ AI Provider .env found")
    
    # Check for OpenAI or Anthropic API key
    if provider_env.exists():
        with open(provider_env) as f:
            content = f.read()
            
            # Look for a valid OpenAI key (starts with sk-)
            has_valid_openai = "OPENAI_API_KEY=sk-" in content
            # Look for a valid Anthropic key
            has_valid_anthropic = "ANTHROPIC_API_KEY=sk-ant-" in content
            # Check for placeholder
            has_placeholder = "your_openai_api_key_here" in content or "your_anthropic" in content
            
            if not (has_valid_openai or has_valid_anthropic):
                if has_placeholder:
                    print("\n WARNING: API key placeholder detected!")
                else:
                    print("\n WARNING: No valid API key found!")
                print("  Add your OpenAI key to uagents_ai_provider/.env")
                print("  Format: OPENAI_API_KEY=sk-proj-your_key_here")
                print("  Or use Anthropic: ANTHROPIC_API_KEY=sk-ant-your_key_here")
                return False
    
    return True

def create_default_env(filepath, agent_type):
    """Create a default .env file"""
    print(f"  Creating default .env for {agent_type}...")
    
    if agent_type == "gateway":
        content = """# Gateway Agent Configuration
GATEWAY_AGENT_SEED=civic_xai_gateway_seed_12345
GATEWAY_AGENT_PORT=8000
API_PORT=8080

# AI Provider Address (will be shown when provider starts)
AI_PROVIDER_AGENT_ADDRESS=agent1qvz2qw3m8kfqj4f7z9q8x6y5t4r3e2w1q

# Optional: Agentverse Integration
# AGENTVERSE_MAILBOX_KEY=your_mailbox_key
AGENT_NETWORK=testnet
"""
    else:  # provider
        content = """# AI Provider Agent Configuration
OPENAI_API_KEY=your_openai_api_key_here
CHAT_MODEL=gpt-4o-mini

AI_PROVIDER_AGENT_SEED=civic_xai_provider_seed_67890
AI_PROVIDER_AGENT_PORT=8001

# Optional: Agentverse Integration
# AGENTVERSE_MAILBOX_KEY=your_mailbox_key
AGENT_NETWORK=testnet
"""
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"  Created: {filepath}")

def run_agents():
    """Run both agents"""
    print_header("Starting uAgents")
    
    base_dir = Path(__file__).parent
    
    print("\n[1] Starting AI Provider Agent...")
    print("    This agent handles allocation calculations and explanations")
    print("    Using OpenAI GPT models and optional MeTTa reasoning")
    
    # Start AI Provider
    provider_cmd = [
        sys.executable,
        str(base_dir / "uagents_ai_provider")
    ]
    
    # Check if enhanced version exists, otherwise use basic
    if not Path(provider_cmd[1]).exists():
        provider_cmd[1] = str(base_dir / "uagents_ai_provider" / "main.py")
    
    try:
        provider_process = subprocess.Popen(
            provider_cmd,
            cwd=str(base_dir / "uagents_ai_provider"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("    ✓ AI Provider started (PID: %d)" % provider_process.pid)
    except Exception as e:
        print(f"    ✗ Failed to start AI Provider: {e}")
        return
    
    # Wait for provider to start
    time.sleep(3)
    
    print("\n[2] Starting Gateway Agent...")
    print("    This agent provides REST API and routes requests")
    print("    API will be available at http://localhost:8080")
    
    # Start Gateway
    gateway_cmd = [
        sys.executable,
        str(base_dir / "uagents_gateway" / "gateway_enhanced.py")
    ]
    
    # Check if enhanced version exists, otherwise use basic
    if not Path(gateway_cmd[1]).exists():
        gateway_cmd[1] = str(base_dir / "uagents_gateway" / "gateway" / "main.py")
    
    try:
        gateway_process = subprocess.Popen(
            gateway_cmd,
            cwd=str(base_dir / "uagents_gateway"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("    ✓ Gateway started (PID: %d)" % gateway_process.pid)
    except Exception as e:
        print(f"    ✗ Failed to start Gateway: {e}")
        provider_process.terminate()
        return
    
    print_header("Agents Running")
    print("\nBoth agents are running!")
    print("\nAPI Endpoints:")
    print("  - Gateway API: http://localhost:8080")
    print("  - API Docs: http://localhost:8080/docs")
    print("\nTest with:")
    print("  curl http://localhost:8080/")
    print("\nPress Ctrl+C to stop all agents...")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping agents...")
        provider_process.terminate()
        gateway_process.terminate()
        print("✓ Agents stopped")

def show_info():
    """Show information about the uAgents implementation"""
    print_header("CivicXAI uAgents Information")
    
    print("""
This implementation uses the uAgents framework for decentralized AI agents.

Components:
1. Gateway Agent - Provides REST API and routes requests
2. AI Provider Agent - Handles calculations and explanations

Based on:
- uAgents Framework: https://docs.agentverse.ai
- ASI:One Standards: https://docs.asi1.ai

Features:
✓ Decentralized agent communication
✓ OpenAI GPT integration
✓ MeTTa symbolic reasoning (optional)
✓ Agentverse network support (optional)
✓ RESTful API interface
✓ Asynchronous processing

To use:
1. Configure OpenAI API key in uagents_ai_provider/.env
2. Run this script to start both agents
3. Access API at http://localhost:8080/docs
    """)

def main():
    """Main function"""
    print_header("CivicXAI uAgents Setup")
    
    # Show info
    show_info()
    
    # Check requirements
    if not check_requirements():
        print("\nPlease install missing requirements first")
        return
    
    # Check configuration
    if not check_env_files():
        print("\nPlease configure .env files before running")
        print("  Especially add your OpenAI API key!")
        return
    
    # Run agents
    try:
        run_agents()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
