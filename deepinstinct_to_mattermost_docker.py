#!/usr/bin/env python3
"""
Deep Instinct to Mattermost Integration (Docker wrapper)
This wrapper modifies environment loading to work in Docker containers
"""

import os
import sys
import importlib.util

# Import everything from original script with path fix
spec = importlib.util.spec_from_file_location("main_module", 
                                               os.path.join(os.path.dirname(__file__), 
                                                          'deepinstinct_to_mattermost.py'))
main_module = importlib.util.module_from_spec(spec)

# Read and patch the original code
original_code = open(os.path.join(os.path.dirname(__file__), 'deepinstinct_to_mattermost.py')).read()

# Replace .env1 with flexible .env
original_code = original_code.replace(
    "load_dotenv('.env1')",
    "load_dotenv(os.getenv('ENV_FILE', '.env'))"
)

# Execute the modified code
exec(original_code, main_module.__dict__)

# Run main if this is the entry point
if __name__ == "__main__":
    main_module.main()
