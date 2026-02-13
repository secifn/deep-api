#!/usr/bin/env python3
"""
Deep Instinct to Mattermost - Daily Report (Docker wrapper)
This wrapper modifies environment loading to work in Docker containers
"""

import os
import sys

# Set up environment for Docker before importing main module
# Docker containers get env vars directly, no need for .env file
# But we still support .env for local testing
if not os.path.exists('.env') and not os.path.exists('.env1'):
    # Running in Docker - create a temporary env file from environment
    # This allows the original script to work without modification
    pass
else:
    # Running locally - use existing .env file
    pass

# Import everything from original script
# First, let's modify the path in the original script to be flexible
import importlib.util
spec = importlib.util.spec_from_file_location("main_module", 
                                               os.path.join(os.path.dirname(__file__), 
                                                          'send_today_to_mattermost.py'))
main_module = importlib.util.module_from_spec(spec)

# Patch the load_dotenv call before executing
original_code = open(os.path.join(os.path.dirname(__file__), 'send_today_to_mattermost.py')).read()

# Replace hardcoded path with flexible path
original_code = original_code.replace(
    "load_dotenv('/home/api/DeepInstint/.env1')",
    "load_dotenv(os.getenv('ENV_FILE', '.env'))"
)

# Execute the modified code
exec(original_code, main_module.__dict__)

# Run main if this is the entry point
if __name__ == "__main__":
    main_module.main()
