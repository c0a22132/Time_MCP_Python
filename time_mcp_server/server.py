#!/usr/bin/env python3
"""
Time MCP Server

A Model Context Protocol server that provides current time information 
for specified countries and timezones.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import pytz
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TimeServerError(Exception):
    """Custom exception for Time Server errors"""
    pass


class TimeServer:
    """Time MCP Server implementation"""

    def __init__(self) -> None:
        self.server = Server("time-mcp-server")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Setup MCP request handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="get_current_time",
                    description="Get the current time for a specified timezone or country",
                    inputSchema={
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
                ),
                Tool(
                    name="list_timezones",
                    description="List available timezones for a specific country or region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "country": {
                                "type": "string",
                                "description": "Country name or country code to filter timezones (optional)",
                            },
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
            """Handle tool calls"""
            try:
                if name == "get_current_time":
                    return await self._handle_get_current_time(arguments)
                elif name == "list_timezones":
                    return await self._handle_list_timezones(arguments)
                else:
                    raise TimeServerError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                raise

    async def _handle_get_current_time(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle get_current_time tool call"""
        timezone_input = args.get("timezone")
        time_format = args.get("format", "%Y-%m-%d %H:%M:%S")

        if not timezone_input:
            raise TimeServerError("Timezone parameter is required")

        try:
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
                raise TimeServerError(
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

            return [
                TextContent(
                    type="text",
                    text=json.dumps(time_data, indent=2, ensure_ascii=False)
                )
            ]

        except Exception as e:
            raise TimeServerError(f"Failed to get current time: {e}")

    async def _handle_list_timezones(self, args: Dict[str, Any]) -> Sequence[TextContent]:
        """Handle list_timezones tool call"""
        country = args.get("country")

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

            return [
                TextContent(
                    type="text",
                    text=json.dumps(timezone_data, indent=2, ensure_ascii=False)
                )
            ]

        except Exception as e:
            raise TimeServerError(f"Failed to list timezones: {e}")

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
        ]        # Search in timezone names
        return [
            tz for tz in extended_timezones 
            if normalized_country in tz.lower() or country.lower() in tz.lower()
        ]

    async def run(self) -> None:
        """Run the MCP server"""
        logger.info("Starting Time MCP server...")
        
        # Use stdio transport for MCP communication
        async with stdio_server() as streams:
            await self.server.run(*streams)


async def main() -> None:
    """Main entry point"""
    server = TimeServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
