#!/usr/bin/env python3
"""
Main entry point for Time MCP Server
"""

import argparse
import asyncio
import os
import sys


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Time MCP Server")
    parser.add_argument(
        "--http", 
        action="store_true", 
        help="Run as HTTP server instead of MCP server"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("PORT", "8080")), 
        help="Port for HTTP server (default: 8080, or PORT environment variable)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host for HTTP server (default: 0.0.0.0, or HOST environment variable)"
    )
    parser.add_argument(
        "--standalone", 
        action="store_true", 
        help="Run standalone version for testing"
    )    
    args = parser.parse_args()
    
    if args.standalone:
        from .standalone import main as standalone_main
        asyncio.run(standalone_main())
    elif args.http:
        try:
            from .http_server import create_app
            import uvicorn
            
            app = create_app()
            print(f"Starting HTTP server on {args.host}:{args.port}")
            uvicorn.run(app, host=args.host, port=args.port)
        except ImportError as e:
            print(f"HTTP server dependencies not available: {e}")
            print("Install with: pip install fastapi uvicorn")
            sys.exit(1)
    else:
        try:
            from .server import main as server_main
            asyncio.run(server_main())
        except ImportError as e:
            print(f"MCP server dependencies not available: {e}")
            print("Falling back to standalone mode...")
            from .standalone import main as standalone_main
            asyncio.run(standalone_main())


if __name__ == "__main__":
    main()
