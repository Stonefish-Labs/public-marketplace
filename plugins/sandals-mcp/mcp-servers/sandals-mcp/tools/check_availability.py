#!/usr/bin/env python3
"""
Room Availability Checker
Checks room availability for specific resorts and date ranges using the Sandals API
"""
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

class AvailabilityChecker:
    """Checks room availability for Sandals resorts"""
    
    def __init__(self):
        self.base_url = "https://www.sandals.com/api/route/resort/rate/price/availability/"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://www.sandals.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
        }
        
        # Load resort data to map codes to brands
        self.resorts = self.load_resort_data()
    
    def load_resort_data(self) -> Dict[str, Any]:
        """Load resort data from JSON file"""
        data_path = Path.cwd() / "data" / "resorts.json"
        if data_path.exists():
            with open(data_path, 'r') as f:
                resorts = json.load(f)
                # Create a mapping from resort_code to resort info
                return {resort['resort_code']: resort for resort in resorts}
        return {}
    
    def get_brand_for_resort(self, resort_code: str) -> str:
        """Get brand code for a resort"""
        # Most are Sandals (S), but some might be Beaches (B)
        if resort_code.startswith('B'):
            return 'B'  # Beaches
        return 'S'  # Sandals
    
    def check_multiple_date_ranges(self, 
                                  resort_code: str, 
                                  start_date: str, 
                                  num_weeks: int = 4, 
                                  stay_length: int = 7, 
                                  adults: int = 2,
                                  children: int = 0) -> List[Dict[str, Any]]:
        """
        Check availability for multiple date ranges
        
        Args:
            resort_code: Resort code (e.g., 'SRB', 'SMB')
            start_date: Starting date in YYYY-MM-DD format
            num_weeks: Number of weeks to check
            stay_length: Length of stay in days
            adults: Number of adults
            children: Number of children
            
        Returns:
            List of availability results for each date range
        """
        results = []
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        
        for week in range(num_weeks):
            check_in_dt = start_dt + timedelta(weeks=week)
            check_out_dt = check_in_dt + timedelta(days=stay_length)
            
            check_in_str = check_in_dt.strftime("%Y-%m-%d")
            check_out_str = check_out_dt.strftime("%Y-%m-%d")
            
            result = self.check_availability(resort_code, check_in_str, check_out_str, adults, children)
            if result["success"]:
                summary = self.get_available_rooms_summary(result)
                result["summary"] = summary
            
            results.append(result)
            
        return results
    
    def validate_children_allowed(self, resort_code: str, children: int) -> bool:
        """Check if resort allows children"""
        if children == 0:
            return True
            
        resort_info = self.resorts.get(resort_code)
        if not resort_info:
            print(f"⚠️  Unknown resort code: {resort_code}")
            return True  # Allow unknown resorts to proceed
            
        kids_allowed = resort_info.get('kids_allowed', False)
        if not kids_allowed and children > 0:
            print(f"❌ {resort_info['name']} does not allow children")
            print(f"   This is an adults-only resort")
            return False
            
        return True
    
    def check_availability(self, 
                          resort_code: str, 
                          check_in: str, 
                          check_out: str, 
                          adults: int = 2,
                          children: int = 0) -> Dict[str, Any]:
        """
        Check availability for a specific resort and date range
        
        Args:
            resort_code: Resort code (e.g., 'SRB', 'SMB')
            check_in: Check-in date in YYYY-MM-DD format
            check_out: Check-out date in YYYY-MM-DD format  
            adults: Number of adults (default 2)
            children: Number of children (default 0)
            
        Returns:
            Dictionary containing availability data or error info
        """
        
        # Validate children are allowed at this resort
        if not self.validate_children_allowed(resort_code, children):
            return {
                "success": False,
                "error": f"Resort {resort_code} does not allow children"
            }
        brand = self.get_brand_for_resort(resort_code)
        
        payload = {
            "brand": brand,
            "resortCode": resort_code,
            "adults": adults,
            "checkIn": check_in,
            "checkOut": check_out
        }
        
        # Add children if specified
        if children > 0:
            payload["children"] = children
        
        print(f"🔍 Checking availability for {resort_code}")
        guest_info = f"{adults} adults"
        if children > 0:
            guest_info += f", {children} children"
        print(f"   📅 {check_in} to {check_out} ({guest_info})")
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully retrieved availability data")
                return {
                    "success": True,
                    "resort_code": resort_code,
                    "check_in": check_in,
                    "check_out": check_out,
                    "adults": adults,
                    "children": children,
                    "data": data
                }
            else:
                print(f"❌ API returned status {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text[:500]
                }
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def parse_availability_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse the availability response to extract room information"""
        if not response_data.get("success"):
            return []
        
        data = response_data.get("data", [])
        if not isinstance(data, list):
            return []
        
        # Parse each room availability record
        parsed_rooms = []
        for room_data in data:
            if isinstance(room_data, dict):
                parsed_room = {
                    "room_category_code": room_data.get("roomCategoryCode", ""),
                    "available": room_data.get("available", False),
                    "available_rooms": room_data.get("availableRooms", 0),
                    "adult_rate": room_data.get("adultRate", 0),
                    "total_price": room_data.get("totalPrice", 0),
                    "total_price_entire_stay": room_data.get("totalPriceForEntireLengthOfStay", 0),
                    "avg_price": room_data.get("avgPriceAdultsAndKids", 0),
                    "length_of_stay": room_data.get("length", 0),
                    "date": room_data.get("date", ""),
                    "unavailable_days": room_data.get("unavailableDays")
                }
                parsed_rooms.append(parsed_room)
        
        return parsed_rooms
    
    def get_available_rooms_summary(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of available rooms"""
        rooms = self.parse_availability_response(response_data)
        
        available_rooms = [room for room in rooms if room["available"]]
        unavailable_rooms = [room for room in rooms if not room["available"]]
        
        summary = {
            "total_room_categories": len(rooms),
            "available_categories": len(available_rooms),
            "unavailable_categories": len(unavailable_rooms),
            "available_rooms": available_rooms,
            "unavailable_rooms": unavailable_rooms
        }
        
        if available_rooms:
            prices = [room["total_price_entire_stay"] for room in available_rooms]
            summary["price_range"] = {
                "min_total_price": min(prices),
                "max_total_price": max(prices),
                "avg_total_price": sum(prices) / len(prices)
            }
        
        return summary
    
    def save_availability_data(self, data: Dict[str, Any], filename: str = None):
        """Save availability data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resort_code = data.get("resort_code", "UNKNOWN")
            filename = f"availability_{resort_code}_{timestamp}.json"
        
        output_path = Path.cwd() / "data" / filename
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved availability data to {output_path}")
        return output_path

def main():
    """Main function for command line usage"""
    import sys
    
    checker = AvailabilityChecker()
    
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python check_availability.py <resort_code> <check_in> <check_out> [adults] [children]")
        print("  python check_availability.py <resort_code> multi <start_date> [num_weeks] [stay_length] [adults] [children]")
        print("\nExamples:")
        print("  python check_availability.py SRB 2025-12-02 2025-12-10")
        print("  python check_availability.py SMB 2025-11-15 2025-11-22 4 0")
        print("  python check_availability.py BTC 2025-11-15 2025-11-22 2 2  # Beaches resort with kids")
        print("  python check_availability.py SMB multi 2025-09-01 4 7 2 0")
        print("\nAvailable resort codes:")
        for code, resort in checker.resorts.items():
            kids_info = "✅ Kids allowed" if resort.get('kids_allowed', False) else "❌ Adults only"
            print(f"  {code} - {resort['name']} ({kids_info})")
        return
    
    resort_code = sys.argv[1].upper()
    mode = sys.argv[2].lower()
    
    if mode == "multi":
        # Multi-date range mode
        if len(sys.argv) < 4:
            print("❌ Multi mode requires at least a start date")
            return
            
        start_date = sys.argv[3]
        num_weeks = int(sys.argv[4]) if len(sys.argv) > 4 else 4
        stay_length = int(sys.argv[5]) if len(sys.argv) > 5 else 7
        adults = int(sys.argv[6]) if len(sys.argv) > 6 else 2
        children = int(sys.argv[7]) if len(sys.argv) > 7 else 0
        
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD")
            return
        
        print(f"🔍 Checking {num_weeks} weeks of availability starting {start_date}")
        guest_info = f"Adults: {adults}"
        if children > 0:
            guest_info += f", Children: {children}"
        print(f"   Stay length: {stay_length} days, {guest_info}")
        
        results = checker.check_multiple_date_ranges(resort_code, start_date, num_weeks, stay_length, adults, children)
        
        print(f"\n📊 Multi-Date Availability Summary for {resort_code}:")
        available_weeks = 0
        
        for i, result in enumerate(results):
            if result["success"] and result.get("summary"):
                summary = result["summary"]
                available_cats = summary["available_categories"]
                
                if available_cats > 0:
                    available_weeks += 1
                    min_price = summary.get("price_range", {}).get("min_total_price", 0)
                    print(f"   Week {i+1} ({result['check_in']} to {result['check_out']}): ✅ {available_cats} categories from ${min_price:,}")
                else:
                    print(f"   Week {i+1} ({result['check_in']} to {result['check_out']}): ❌ No availability")
            else:
                print(f"   Week {i+1}: ❌ Failed to check")
        
        print(f"\n🎯 {available_weeks}/{len(results)} weeks have availability")
        
    else:
        # Single date range mode
        check_in = mode  # sys.argv[2] is actually check_in
        check_out = sys.argv[3]
        adults = int(sys.argv[4]) if len(sys.argv) > 4 else 2
        children = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        
        # Validate date format
        try:
            datetime.strptime(check_in, "%Y-%m-%d")
            datetime.strptime(check_out, "%Y-%m-%d")
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD")
            return
        
        # Check availability
        result = checker.check_availability(resort_code, check_in, check_out, adults, children)
        
        if result["success"]:
            # Save the raw data (commented out to avoid file spam)
            # saved_path = checker.save_availability_data(result)
            
            # Get detailed summary
            summary = checker.get_available_rooms_summary(result)
            
            print(f"\n📋 Availability Summary:")
            print(f"   Resort: {resort_code}")
            print(f"   Dates: {check_in} to {check_out}")
            guest_summary = f"   Adults: {adults}"
            if children > 0:
                guest_summary += f", Children: {children}"
            print(guest_summary)
            print(f"   Total room categories: {summary['total_room_categories']}")
            print(f"   Available categories: {summary['available_categories']}")
            print(f"   Unavailable categories: {summary['unavailable_categories']}")
            
            if summary['available_rooms']:
                print(f"\n✅ Available Rooms:")
                for room in summary['available_rooms']:
                    print(f"   {room['room_category_code']}: {room['available_rooms']} rooms - ${room['total_price_entire_stay']:,} total")
                
                price_range = summary.get('price_range', {})
                if price_range:
                    print(f"\n💰 Price Range:")
                    print(f"   Min: ${price_range['min_total_price']:,}")
                    print(f"   Max: ${price_range['max_total_price']:,}")
                    print(f"   Avg: ${price_range['avg_total_price']:,.0f}")
            else:
                print(f"\n❌ No rooms available for these dates")
                
            # print(f"\n💾 Full data saved to: {saved_path}")  # Commented out
        else:
            print(f"\n❌ Failed to get availability data")
            print(f"   Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
