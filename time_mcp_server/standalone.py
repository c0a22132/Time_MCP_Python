#!/usr/bin/env python3
"""
Time Server - Standalone Implementation

A simple time server that can work without MCP dependencies for testing.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Fallback timezone implementation without pytz
class SimpleTimezone:
    """Simple timezone implementation using standard library"""
    
    TIMEZONE_OFFSETS = {
        "UTC": 0,
        "GMT": 0,
        "Asia/Tokyo": 9,
        "Asia/Seoul": 9,
        "Asia/Shanghai": 8,
        "Asia/Hong_Kong": 8,
        "Asia/Singapore": 8,
        "Asia/Bangkok": 7,
        "Asia/Jakarta": 7,
        "Asia/Kolkata": 5.5,
        "Asia/Mumbai": 5.5,
        "Asia/Dubai": 4,
        "Asia/Karachi": 5,
        "Europe/London": 0,  # Note: This doesn't handle DST
        "Europe/Berlin": 1,
        "Europe/Paris": 1,
        "Europe/Rome": 1,
        "Europe/Madrid": 1,
        "Europe/Amsterdam": 1,
        "Europe/Brussels": 1,
        "Europe/Vienna": 1,
        "Europe/Zurich": 1,
        "Europe/Stockholm": 1,
        "Europe/Oslo": 1,
        "Europe/Copenhagen": 1,
        "Europe/Helsinki": 2,
        "Europe/Moscow": 3,
        "Europe/Istanbul": 3,
        "Europe/Athens": 2,
        "America/New_York": -5,  # Note: This doesn't handle DST
        "America/Chicago": -6,
        "America/Denver": -7,
        "America/Los_Angeles": -8,
        "America/Anchorage": -9,
        "America/Toronto": -5,
        "America/Vancouver": -8,
        "America/Edmonton": -7,
        "America/Winnipeg": -6,
        "America/Halifax": -4,
        "America/Mexico_City": -6,
        "America/Sao_Paulo": -3,
        "America/Buenos_Aires": -3,
        "America/Lima": -5,
        "America/Bogota": -5,
        "America/Santiago": -4,
        "America/Caracas": -4,
        "Australia/Sydney": 10,  # Note: This doesn't handle DST
        "Australia/Melbourne": 10,
        "Australia/Perth": 8,
        "Australia/Adelaide": 9.5,
        "Australia/Darwin": 9.5,
        "Pacific/Auckland": 12,
        "Pacific/Honolulu": -10,
        "Africa/Cairo": 2,
        "Africa/Lagos": 1,
        "Africa/Johannesburg": 2,
        "Africa/Casablanca": 1,
        "Africa/Nairobi": 3,
    }

    @classmethod
    def get_timezone_offset(cls, timezone: str) -> Optional[float]:
        """Get timezone offset in hours"""
        return cls.TIMEZONE_OFFSETS.get(timezone)

    @classmethod
    def get_current_time(cls, timezone: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Dict[str, Any]:
        """Get current time for timezone"""
        offset = cls.get_timezone_offset(timezone)
        if offset is None:
            raise ValueError(f"Unknown timezone: {timezone}")
        
        utc_now = datetime.utcnow()
        
        # Calculate local time (simplified, doesn't handle DST properly)
        hours_offset = int(offset)
        minutes_offset = int((offset - hours_offset) * 60)
        
        import datetime as dt
        local_time = utc_now + dt.timedelta(hours=hours_offset, minutes=minutes_offset)
        
        # Format offset string
        sign = "+" if offset >= 0 else "-"
        abs_offset = abs(offset)
        offset_hours = int(abs_offset)
        offset_minutes = int((abs_offset - offset_hours) * 60)
        utc_offset = f"{sign}{offset_hours:02d}{offset_minutes:02d}"
        
        return {
            "timezone": timezone,
            "current_time": local_time.strftime(format_str),
            "timezone_name": timezone.split("/")[-1],
            "utc_offset": utc_offset,
            "timestamp": int(local_time.timestamp()),
            "iso_string": local_time.isoformat(),
        }

    @classmethod
    def list_timezones(cls) -> List[str]:
        """List all available timezones"""
        return sorted(cls.TIMEZONE_OFFSETS.keys())


class TimeServerStandalone:
    """Standalone time server implementation"""

    def __init__(self):
        self.timezone_helper = SimpleTimezone()

    def get_timezones_by_country(self, country: str) -> List[str]:
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

        # Search in timezone names
        all_timezones = self.timezone_helper.list_timezones()
        return [
            tz for tz in all_timezones 
            if normalized_country in tz.lower() or country.lower() in tz.lower()
        ]

    def get_current_time(self, timezone_input: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Dict[str, Any]:
        """Get current time for timezone or country"""
        if not timezone_input:
            raise ValueError("Timezone parameter is required")

        # Try to find timezone by name or country
        target_timezone = timezone_input
        
        # If it's a country name, try to get the main timezone
        country_timezones = self.get_timezones_by_country(timezone_input)
        if country_timezones:
            target_timezone = country_timezones[0]

        try:
            return self.timezone_helper.get_current_time(target_timezone, format_str)
        except ValueError as e:
            available_timezones = self.timezone_helper.list_timezones()[:10]  # Show first 10
            raise ValueError(f"{e}. Available timezones include: {', '.join(available_timezones)}...")

    def list_timezones(self, country: Optional[str] = None) -> Dict[str, Any]:
        """List available timezones"""
        if country:
            timezones = self.get_timezones_by_country(country)
        else:
            timezones = self.timezone_helper.list_timezones()

        return {
            "query": country or "all",
            "total_timezones": len(timezones),
            "timezones": sorted(timezones),
        }

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Handle tool calls (simulating MCP interface)"""
        try:
            if tool_name == "get_current_time":
                timezone = arguments.get("timezone")
                format_str = arguments.get("format", "%Y-%m-%d %H:%M:%S")
                result = self.get_current_time(timezone, format_str)
                return json.dumps(result, indent=2, ensure_ascii=False)
                
            elif tool_name == "list_timezones":
                country = arguments.get("country")
                result = self.list_timezones(country)
                return json.dumps(result, indent=2, ensure_ascii=False)
                
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            error_result = {"error": str(e)}
            return json.dumps(error_result, indent=2, ensure_ascii=False)

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools"""
        return [
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


async def main():
    """Main function for testing"""
    server = TimeServerStandalone()
    
    # Test cases
    print("=== Time MCP Server (Standalone) ===\n")
    
    print("Available tools:")
    tools = server.get_tools()
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    print()
    
    # Test get_current_time
    print("Testing get_current_time:")
    test_cases = [
        {"timezone": "Japan"},
        {"timezone": "Asia/Tokyo", "format": "%Y/%m/%d %H:%M:%S"},
        {"timezone": "United States"},
        {"timezone": "UTC"},
    ]
    
    for test_case in test_cases:
        print(f"Input: {test_case}")
        result = await server.handle_tool_call("get_current_time", test_case)
        print(f"Output: {result}\n")
    
    # Test list_timezones
    print("Testing list_timezones:")
    timezone_test_cases = [
        {},
        {"country": "Japan"},
        {"country": "United States"},
    ]
    
    for test_case in timezone_test_cases:
        print(f"Input: {test_case}")
        result = await server.handle_tool_call("list_timezones", test_case)
        print(f"Output: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())
