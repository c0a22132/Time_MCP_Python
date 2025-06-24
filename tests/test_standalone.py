"""
Tests for the standalone time server
"""

import asyncio
import json
import pytest
from datetime import datetime

from time_mcp_server.standalone import TimeServerStandalone, SimpleTimezone


class TestSimpleTimezone:
    """Tests for SimpleTimezone class"""

    def test_get_timezone_offset(self):
        """Test timezone offset retrieval"""
        assert SimpleTimezone.get_timezone_offset("UTC") == 0
        assert SimpleTimezone.get_timezone_offset("Asia/Tokyo") == 9
        assert SimpleTimezone.get_timezone_offset("America/New_York") == -5
        assert SimpleTimezone.get_timezone_offset("Invalid/Timezone") is None

    def test_get_current_time(self):
        """Test current time retrieval"""
        result = SimpleTimezone.get_current_time("UTC")
        
        assert "timezone" in result
        assert "current_time" in result
        assert "timezone_name" in result
        assert "utc_offset" in result
        assert "timestamp" in result
        assert "iso_string" in result
        
        assert result["timezone"] == "UTC"
        assert result["utc_offset"] == "+0000"

    def test_get_current_time_with_format(self):
        """Test current time with custom format"""
        result = SimpleTimezone.get_current_time("UTC", "%Y/%m/%d")
        
        # Check that the format is applied
        assert len(result["current_time"].split("/")) == 3

    def test_get_current_time_invalid_timezone(self):
        """Test current time with invalid timezone"""
        with pytest.raises(ValueError, match="Unknown timezone"):
            SimpleTimezone.get_current_time("Invalid/Timezone")

    def test_list_timezones(self):
        """Test timezone listing"""
        timezones = SimpleTimezone.list_timezones()
        
        assert isinstance(timezones, list)
        assert len(timezones) > 0
        assert "UTC" in timezones
        assert "Asia/Tokyo" in timezones
        
        # Check that list is sorted
        assert timezones == sorted(timezones)


class TestTimeServerStandalone:
    """Tests for TimeServerStandalone class"""

    def setup_method(self):
        """Setup test server"""
        self.server = TimeServerStandalone()

    def test_get_timezones_by_country(self):
        """Test country to timezone mapping"""
        # Test direct mapping
        japan_timezones = self.server.get_timezones_by_country("Japan")
        assert "Asia/Tokyo" in japan_timezones
        
        usa_timezones = self.server.get_timezones_by_country("United States")
        assert "America/New_York" in usa_timezones
        assert "America/Los_Angeles" in usa_timezones
        
        # Test case insensitive
        uk_timezones = self.server.get_timezones_by_country("uk")
        assert "Europe/London" in uk_timezones

    def test_get_current_time(self):
        """Test current time retrieval"""
        # Test with timezone
        result = self.server.get_current_time("UTC")
        assert isinstance(result, dict)
        assert result["timezone"] == "UTC"
        
        # Test with country
        result = self.server.get_current_time("Japan")
        assert result["timezone"] == "Asia/Tokyo"

    def test_get_current_time_invalid(self):
        """Test current time with invalid input"""
        with pytest.raises(ValueError):
            self.server.get_current_time("")
        
        with pytest.raises(ValueError):
            self.server.get_current_time("Invalid/Country")

    def test_list_timezones(self):
        """Test timezone listing"""
        # Test all timezones
        result = self.server.list_timezones()
        assert isinstance(result, dict)
        assert "total_timezones" in result
        assert "timezones" in result
        assert result["query"] == "all"
        
        # Test country filter
        result = self.server.list_timezones("Japan")
        assert result["query"] == "Japan"
        assert "Asia/Tokyo" in result["timezones"]

    @pytest.mark.asyncio
    async def test_handle_tool_call_get_current_time(self):
        """Test tool call handling for get_current_time"""
        result = await self.server.handle_tool_call(
            "get_current_time",
            {"timezone": "UTC"}
        )
        
        data = json.loads(result)
        assert "timezone" in data
        assert data["timezone"] == "UTC"

    @pytest.mark.asyncio
    async def test_handle_tool_call_list_timezones(self):
        """Test tool call handling for list_timezones"""
        result = await self.server.handle_tool_call(
            "list_timezones",
            {"country": "Japan"}
        )
        
        data = json.loads(result)
        assert "timezones" in data
        assert "Asia/Tokyo" in data["timezones"]

    @pytest.mark.asyncio
    async def test_handle_tool_call_invalid_tool(self):
        """Test tool call handling for invalid tool"""
        result = await self.server.handle_tool_call(
            "invalid_tool",
            {}
        )
        
        data = json.loads(result)
        assert "error" in data

    def test_get_tools(self):
        """Test tool definition retrieval"""
        tools = self.server.get_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 2
        
        tool_names = [tool["name"] for tool in tools]
        assert "get_current_time" in tool_names
        assert "list_timezones" in tool_names
        
        # Check tool structure
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
