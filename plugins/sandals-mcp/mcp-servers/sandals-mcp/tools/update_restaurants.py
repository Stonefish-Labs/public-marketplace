#!/usr/bin/env python3
"""
Restaurant Data Updater
Updates restaurant data for specific resort codes in restaurants.json
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from tools.rsc_base import RSCParser, build_rsc_url, get_brand_for_resort

class RestaurantUpdater:
    """Updates restaurant data for resorts"""
    
    def __init__(self, output_file: str = "restaurants.json"):
        self.output_file = Path(output_file)
        self.parser = RSCParser()
        
        # Field patterns to identify restaurant objects
        self.restaurant_fields = [
            'restaurantName', 'cuisineType', 'dressCode', 'restaurantDescription',
            'restaurantBreakfast', 'restaurantLunch', 'restaurantDinner'
        ]
    
    def load_existing_data(self) -> Dict[str, Any]:
        """Load existing restaurant data or create empty dict"""
        if self.output_file.exists():
            with open(self.output_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_data(self, data: Dict[str, Any]):
        """Save restaurant data to file"""
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved restaurant data to {self.output_file}")
    
    def extract_restaurants_from_rsc(self, resort_code: str) -> List[Dict[str, Any]]:
        """Extract restaurant data for a specific resort"""
        brand = get_brand_for_resort(resort_code)
        url = build_rsc_url(brand, resort_code, 'restaurants')
        
        print(f"🔍 Fetching restaurant data for {resort_code}...")
        response_text = self.parser.fetch_rsc_data(url)
        if not response_text:
            return []
        
        chunks = self.parser.parse_rsc_response(response_text)
        raw_restaurants = self.parser.analyze_rsc_content(chunks, 'restaurants', self.restaurant_fields)
        
        # Convert to standardized format
        standardized_restaurants = []
        
        for restaurant in raw_restaurants:
            # Skip if this doesn't look like a complete restaurant object
            if not restaurant.get('restaurantName') and not restaurant.get('name'):
                continue
                
            # Convert to our standard format
            standardized = {
                "name": restaurant.get('restaurantName', restaurant.get('name', 'Unknown')),
                "cuisine_type": restaurant.get('cuisineType', restaurant.get('cuisine_type', 'Unknown')),
                "dress_code": restaurant.get('dressCode', restaurant.get('dress_code', 'Resort Casual')),
                "description": restaurant.get('restaurantDescription', restaurant.get('description', '')),
                "short_description": restaurant.get('restaurantShortDescription', restaurant.get('short_description', '')),
                "reservation_required": restaurant.get('restaurantReservation') == 'YES' or restaurant.get('reservation_required', False),
                "breakfast": restaurant.get('restaurantBreakfast') == 'YES' or restaurant.get('breakfast', False),
                "lunch": restaurant.get('restaurantLunch') == 'YES' or restaurant.get('lunch', False),
                "dinner": restaurant.get('restaurantDinner') == 'YES' or restaurant.get('dinner', False),
                "hours": [],
                "menus": []
            }
            
            # Extract hours from the restaurant data
            hours_list = []
            if restaurant.get('restaurantBreakfast') == 'YES' and restaurant.get('restaurantBreakfastDescription'):
                hours_list.append(f"Breakfast: {restaurant['restaurantBreakfastDescription']}")
            if restaurant.get('restaurantLunch') == 'YES' and restaurant.get('restaurantLunchDescription'):
                hours_list.append(f"Lunch: {restaurant['restaurantLunchDescription']}")
            if restaurant.get('restaurantDinner') == 'YES' and restaurant.get('restaurantDinnerDescription'):
                hours_list.append(f"Dinner: {restaurant['restaurantDinnerDescription']}")
            
            if hours_list:
                standardized['hours'] = hours_list
            
            # Extract menu URLs if available
            if restaurant.get('restaurantMenu'):
                menu_url = restaurant['restaurantMenu']
                if not menu_url.startswith('http'):
                    # Construct full URL based on brand
                    brand = get_brand_for_resort(resort_code)
                    if brand == 'beaches':
                        menu_url = f"https://cdn.sandals.com/beaches/v11/media/{resort_code.lower()}/restaurants/menus/{menu_url}"
                    else:
                        menu_url = f"https://cdn.sandals.com/sandals/v11/media/{resort_code.lower()}/restaurants/menus/{menu_url}"
                standardized['menus'] = [menu_url]
            
            standardized_restaurants.append(standardized)
        
        print(f"✅ Found {len(standardized_restaurants)} restaurants for {resort_code}")
        return standardized_restaurants
    
    def update_resort(self, resort_code: str) -> bool:
        """Update restaurant data for a specific resort. Returns True if successful."""
        print(f"\n🔄 Updating restaurants for {resort_code}...")
        
        # Load existing data
        all_data = self.load_existing_data()
        
        # Extract new restaurant data
        restaurants = self.extract_restaurants_from_rsc(resort_code)
        
        if restaurants:
            # Update the data for this resort
            all_data[resort_code] = restaurants
            self.save_data(all_data)
            print(f"✅ Updated {len(restaurants)} restaurants for {resort_code}")
            return True
        else:
            print(f"⚠️  No restaurants found for {resort_code}")
            return False
    
    def update_all_resorts(self):
        """Update restaurant data for all resorts"""
        from tools.rsc_base import RESORT_CODES
        
        print("🚀 Updating restaurants for all resorts...")
        
        all_resort_codes = []
        for brand_resorts in RESORT_CODES.values():
            all_resort_codes.extend(brand_resorts.keys())
        
        successful = 0
        failed = 0
        
        for resort_code in all_resort_codes:
            try:
                if self.update_resort(resort_code):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Failed to update {resort_code}: {str(e)}")
                failed += 1
        
        print(f"\n🎉 Restaurant update complete!")
        print(f"✅ Successful: {successful} resorts")
        print(f"❌ Failed: {failed} resorts")

def main():
    """Main function for command line usage"""
    import sys
    # Set up a path relative to cwd as data/restaurants.json
    data_path = Path.cwd() / "data" / "restaurants.json"
    updater = RestaurantUpdater(data_path)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_restaurants.py <resort_code>  # Update specific resort")
        print("  python update_restaurants.py all            # Update all resorts")
        print("\nExamples:")
        print("  python update_restaurants.py BTC")
        print("  python update_restaurants.py SRB")
        print("  python update_restaurants.py all")
        return
    
    if sys.argv[1].lower() == 'all':
        updater.update_all_resorts()
    else:
        resort_code = sys.argv[1].upper()
        updater.update_resort(resort_code)

if __name__ == "__main__":
    main()
