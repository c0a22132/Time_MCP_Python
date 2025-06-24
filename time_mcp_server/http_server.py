#!/usr/bin/env python3
"""
HTTP Server for Time MCP

A FastAPI-based HTTP server that exposes time functionality via REST API.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeHTTPServer:
    """HTTP Server for time functionality"""

    def __init__(self) -> None:
        self.app = FastAPI(
            title="Time MCP Server",
            description="HTTP API for time and timezone functionality",
            version="1.0.0",
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup HTTP routes"""

        @self.app.get("/")
        async def root() -> Dict[str, str]:
            """Root endpoint"""
            return {
                "service": "time-mcp-server",
                "version": "1.0.0",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
            }

        @self.app.get("/health")
        async def health_check() -> Dict[str, str]:
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "time-mcp-server",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
            }

        @self.app.get("/time/{timezone}")
        async def get_time(
            timezone: str, 
            format: Optional[str] = Query(default="%Y-%m-%d %H:%M:%S", description="Time format")
        ) -> JSONResponse:
            """Get current time for specified timezone"""
            try:
                # Try to find timezone by name or country
                target_timezone = timezone
                
                # If it's a country name, try to get the main timezone
                country_timezones = self._get_timezones_by_country(timezone)
                if country_timezones:
                    target_timezone = country_timezones[0]

                # Validate timezone
                try:
                    tz = pytz.timezone(target_timezone)
                except pytz.UnknownTimeZoneError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid timezone: {timezone}. Use /timezones endpoint to see available timezones."
                    )

                # Get current time
                utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
                local_time = utc_now.astimezone(tz)
                
                # Prepare response data
                time_data = {
                    "timezone": target_timezone,
                    "current_time": local_time.strftime(format),
                    "timezone_name": local_time.strftime("%Z"),
                    "utc_offset": local_time.strftime("%z"),
                    "timestamp": int(local_time.timestamp()),
                    "iso_string": local_time.isoformat(),
                }

                return JSONResponse(content=time_data)

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting time for {timezone}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get current time: {str(e)}"
                )

        @self.app.get("/timezones")
        async def list_timezones(
            country: Optional[str] = Query(default=None, description="Country name to filter timezones")
        ) -> JSONResponse:
            """List available timezones"""
            try:
                if country:
                    timezones = self._get_timezones_by_country(country)
                else:
                    timezones = pytz.all_timezones

                timezone_list = sorted(list(timezones))

                timezone_data = {
                    "query": country or "all",
                    "total_timezones": len(timezone_list),
                    "timezones": timezone_list,
                }

                return JSONResponse(content=timezone_data)

            except Exception as e:
                logger.error(f"Error listing timezones: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to list timezones: {str(e)}"
                )

        @self.app.post("/mcp")
        async def mcp_endpoint(request: Request) -> JSONResponse:
            """MCP protocol endpoint for VS Code extension"""
            try:
                body = await request.json()
                logger.info(f"Received MCP request: {body}")
                
                # Handle MCP JSON-RPC 2.0 protocol
                if "method" not in body:
                    return JSONResponse(
                        status_code=400,
                        content={"error": {"code": -32600, "message": "Invalid Request"}}
                    )
                
                method = body["method"]
                params = body.get("params", {})
                request_id = body.get("id")
                
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": "time-mcp-server",
                                "version": "1.0.0"
                            }
                        }
                    }
                elif method == "tools/list":
                    tools = [
                        {
                            "name": "get_current_time",
                            "description": "Get the current time for a specified timezone or country",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "timezone": {
                                        "type": "string",
                                        "description": "Timezone name (e.g., 'Asia/Tokyo', 'America/New_York') or country name (e.g., 'Japan', 'United States')",
                                    },
                                    "format": {
                                        "type": "string",
                                        "description": "Time format (optional, defaults to '%Y-%m-%d %H:%M:%S')",
                                        "default": "%Y-%m-%d %H:%M:%S",
                                    },
                                },
                                "required": ["timezone"],
                            },
                        },
                        {
                            "name": "list_timezones",
                            "description": "List available timezones for a specific country or region",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "country": {
                                        "type": "string",
                                        "description": "Country name or country code to filter timezones (optional)",
                                    },
                                },
                            },
                        },
                    ]
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": tools
                        }
                    }
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    try:
                        if tool_name == "get_current_time":
                            result = await self._handle_mcp_get_current_time(arguments)
                        elif tool_name == "list_timezones":
                            result = await self._handle_mcp_list_timezones(arguments)
                        else:
                            raise ValueError(f"Unknown tool: {tool_name}")
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": result
                                    }
                                ]
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32603,
                                "message": f"Internal error: {str(e)}"
                            }
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                logger.info(f"Sending MCP response: {response}")
                return JSONResponse(content=response)
                
            except Exception as e:
                logger.error(f"Error in MCP endpoint: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "jsonrpc": "2.0",
                        "id": body.get("id") if 'body' in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                )

    def _get_timezones_by_country(self, country: str) -> List[str]:
        """Get timezones for a specific country"""
        country_mappings = {
            "utc": ["UTC"],
            "gmt": ["GMT", "UTC"],
            "japan": ["Asia/Tokyo"],
            "united states": [
                "America/New_York", "America/Chicago", "America/Denver", 
                "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu"
            ],
            "usa": [
                "America/New_York", "America/Chicago", "America/Denver", 
                "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu"
            ],
            "china": ["Asia/Shanghai", "Asia/Hong_Kong"],
            "united kingdom": ["Europe/London"],
            "uk": ["Europe/London"],
            "germany": ["Europe/Berlin"],
            "france": ["Europe/Paris"],
            "italy": ["Europe/Rome"],
            "spain": ["Europe/Madrid"],
            "australia": [
                "Australia/Sydney", "Australia/Melbourne", "Australia/Perth", 
                "Australia/Adelaide", "Australia/Darwin"
            ],
            "canada": [
                "America/Toronto", "America/Vancouver", "America/Edmonton", 
                "America/Winnipeg", "America/Halifax"
            ],
            "india": ["Asia/Kolkata", "Asia/Mumbai"],
            "brazil": ["America/Sao_Paulo"],
            "russia": ["Europe/Moscow"],
            "south korea": ["Asia/Seoul"],
            "korea": ["Asia/Seoul"],
            "mexico": ["America/Mexico_City"],
            "argentina": ["America/Buenos_Aires"],
            "egypt": ["Africa/Cairo"],
            "south africa": ["Africa/Johannesburg"],
            "new zealand": ["Pacific/Auckland"],
            "singapore": ["Asia/Singapore"],
            "thailand": ["Asia/Bangkok"],
            "indonesia": ["Asia/Jakarta"],
            "pakistan": ["Asia/Karachi"],
            "uae": ["Asia/Dubai"],
            "netherlands": ["Europe/Amsterdam"],
            "belgium": ["Europe/Brussels"],
            "austria": ["Europe/Vienna"],
            "switzerland": ["Europe/Zurich"],
            "sweden": ["Europe/Stockholm"],
            "norway": ["Europe/Oslo"],
            "denmark": ["Europe/Copenhagen"],
            "finland": ["Europe/Helsinki"],
            "turkey": ["Europe/Istanbul"],
            "greece": ["Europe/Athens"],
            "peru": ["America/Lima"],
            "colombia": ["America/Bogota"],
            "chile": ["America/Santiago"],
            "venezuela": ["America/Caracas"],
            "nigeria": ["Africa/Lagos"],
            "kenya": ["Africa/Nairobi"],
            "morocco": ["Africa/Casablanca"],
        }

        normalized_country = country.lower()
        
        # Direct mapping
        if normalized_country in country_mappings:
            return country_mappings[normalized_country]

        # Extended timezone list for fallback search
        extended_timezones = [
            "UTC", "GMT",
            "Asia/Tokyo", "Asia/Seoul", "Asia/Shanghai", "Asia/Hong_Kong", "Asia/Singapore",
            "Asia/Bangkok", "Asia/Jakarta", "Asia/Kolkata", "Asia/Mumbai", "Asia/Dubai",
            "Asia/Karachi", "Australia/Sydney", "Australia/Melbourne", "Australia/Perth",
            "Australia/Adelaide", "Australia/Darwin", "Pacific/Auckland", "Pacific/Honolulu",
            "Europe/London", "Europe/Berlin", "Europe/Paris", "Europe/Rome", "Europe/Madrid",
            "Europe/Amsterdam", "Europe/Brussels", "Europe/Vienna", "Europe/Zurich",
            "Europe/Stockholm", "Europe/Oslo", "Europe/Copenhagen", "Europe/Helsinki",
            "Europe/Moscow", "Europe/Istanbul", "Europe/Athens",
            "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
            "America/Anchorage", "America/Toronto", "America/Vancouver", "America/Edmonton",
            "America/Winnipeg", "America/Halifax", "America/Mexico_City",
            "America/Sao_Paulo", "America/Buenos_Aires", "America/Lima", "America/Bogota",
            "America/Santiago", "America/Caracas",
            "Africa/Cairo", "Africa/Lagos", "Africa/Johannesburg", "Africa/Casablanca",
            "Africa/Nairobi"
        ]

        # Search in timezone names
        return [
            tz for tz in extended_timezones            if normalized_country in tz.lower() or country.lower() in tz.lower()
        ]

    async def _handle_mcp_get_current_time(self, args: Dict[str, Any]) -> str:
        """Handle MCP get_current_time request"""
        timezone_input = args.get("timezone")
        time_format = args.get("format", "%Y-%m-%d %H:%M:%S")

        if not timezone_input:
            raise ValueError("Timezone parameter is required")

        # Try to find timezone by name or country
        target_timezone = timezone_input
        
        # If it's a country name, try to get the main timezone
        country_timezones = self._get_timezones_by_country(timezone_input)
        if country_timezones:
            target_timezone = country_timezones[0]

        # Validate timezone
        try:
            tz = pytz.timezone(target_timezone)
        except pytz.UnknownTimeZoneError:
            raise ValueError(
                f"Invalid timezone: {timezone_input}. Use list_timezones tool to see available timezones."
            )

        # Get current time
        utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        local_time = utc_now.astimezone(tz)
        
        # Prepare response data
        time_data = {
            "timezone": target_timezone,
            "current_time": local_time.strftime(time_format),
            "timezone_name": local_time.strftime("%Z"),
            "utc_offset": local_time.strftime("%z"),
            "timestamp": int(local_time.timestamp()),
            "iso_string": local_time.isoformat(),
        }

        return json.dumps(time_data, indent=2, ensure_ascii=False)

    async def _handle_mcp_list_timezones(self, args: Dict[str, Any]) -> str:
        """Handle MCP list_timezones request"""
        country = args.get("country")

        if country:
            timezones = self._get_timezones_by_country(country)
        else:
            timezones = pytz.all_timezones

        timezone_list = sorted(list(timezones))

        timezone_data = {
            "query": country or "all",
            "total_timezones": len(timezone_list),
            "timezones": timezone_list,
        }

        return json.dumps(timezone_data, indent=2, ensure_ascii=False)


def create_app() -> FastAPI:
    """Create FastAPI application"""
    server = TimeHTTPServer()
    return server.app


# For uvicorn factory pattern
app = create_app()


if __name__ == "__main__":
    import os
    import uvicorn
    
    app = create_app()
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
