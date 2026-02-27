#!/usr/bin/env python3
"""
Room Data Updater
Updates room data for specific resort codes in rooms.json
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from tools.rsc_base import RSCParser, build_rsc_url, get_brand_for_resort

class RoomUpdater:
    """Updates room data for resorts"""
    
    def __init__(self, output_file: str = "rooms.json"):
        self.output_file = Path(output_file)
        self.parser = RSCParser()
        
        # Field patterns to identify room objects
        self.room_fields = [
            'categoryCode', 'categoryId', 'resortName', 'rstCode',
            'name', 'description', 'bedding', 'maxOccupancy'
        ]
    
    def load_existing_data(self) -> Dict[str, Any]:
        """Load existing room data or create empty dict"""
        if self.output_file.exists():
            with open(self.output_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_data(self, data: Dict[str, Any]):
        """Save room data to file"""
        with open(self.output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved room data to {self.output_file}")
    
    def extract_rooms_from_rsc(self, resort_code: str) -> List[Dict[str, Any]]:
        """Extract room data for a specific resort"""
        brand = get_brand_for_resort(resort_code)
        url = build_rsc_url(brand, resort_code, 'rooms')
        
        print(f"🔍 Fetching room data for {resort_code}...")
        response_text = self.parser.fetch_rsc_data(url)
        if not response_text:
            return []
        
        chunks = self.parser.parse_rsc_response(response_text)
        
        # Find room data chunks - look for objects with categoryCode
        raw_rooms = []
        
        for chunk_id, chunk_data in chunks.items():
            if isinstance(chunk_data, dict) and 'categoryCode' in chunk_data:
                # This looks like a room object, resolve all its references
                resolved_room = self.parser.resolve_references(chunk_data, chunks)
                raw_rooms.append(resolved_room)
        
        # Clean up the room data
        cleaned_rooms = []
        for room in raw_rooms:
            cleaned_room = self.clean_room_data(room)
            cleaned_rooms.append(cleaned_room)
        
        print(f"✅ Found {len(cleaned_rooms)} rooms for {resort_code}")
        return cleaned_rooms
    
    def clean_room_data(self, room: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up room data by removing unnecessary fields and simplifying structure"""
        cleaned = {
            "room_code": room.get('categoryCode', ''),
            "name": room.get('name', ''),
            "description": room.get('description', ''),
            "bedding": room.get('bedding', ''),
            "max_occupancy": room.get('maxOccupancy', 0),
            "max_adults": room.get('maxAdults', 0),
            "room_class": room.get('roomClass', ''),
            "transfer_type": room.get('transferType', 'Airport')
        }
        
        # Clean up amenities - just get the names
        if 'amenities' in room and isinstance(room['amenities'], list):
            amenity_names = []
            for amenity in room['amenities']:
                if isinstance(amenity, dict):
                    name = amenity.get('amenityName', amenity.get('name', ''))
                    if name and name not in amenity_names:
                        amenity_names.append(name)
            cleaned['amenities'] = amenity_names
        else:
            cleaned['amenities'] = []
        
        # Clean up images - extract from slider and main image
        image_urls = []
        
        # Get main image URL if it exists
        if 'image' in room and isinstance(room['image'], str):
            image_urls.append(room['image'])
        elif 'image' in room and isinstance(room['image'], dict):
            url = room['image'].get('url', '')
            if url:
                image_urls.append(url)
        
        # Get slider images
        if 'images' in room and isinstance(room['images'], dict):
            slider = room['images'].get('slider', [])
            if isinstance(slider, list):
                for image in slider:
                    if isinstance(image, dict):
                        url = image.get('url', '')
                        if url and url not in image_urls:
                            image_urls.append(url)
        elif 'images' in room and isinstance(room['images'], list):
            # Handle case where images is a direct list
            for image in room['images']:
                if isinstance(image, dict):
                    url = image.get('url', image.get('src', ''))
                    if url and url not in image_urls:
                        image_urls.append(url)
        
        cleaned['images'] = image_urls
        
        # Clean up attributes - keep name and description only
        if 'attributes' in room and isinstance(room['attributes'], list):
            clean_attributes = []
            for attr in room['attributes']:
                if isinstance(attr, dict):
                    clean_attr = {
                        'name': attr.get('name', ''),
                        'description': attr.get('description', '')
                    }
                    # Only include if it has meaningful content
                    if clean_attr['name'] or clean_attr['description']:
                        clean_attributes.append(clean_attr)
            cleaned['attributes'] = clean_attributes
        else:
            cleaned['attributes'] = []
        
        # Process overview info - convert to key-value pairs
        if 'overview' in room and isinstance(room['overview'], list):
            for item in room['overview']:
                if isinstance(item, dict) and 'label' in item and 'value' in item:
                    label = item['label']
                    value = item['value']
                    
                    # Convert specific labels to useful fields
                    if label == "Room View(s)" and value:
                        cleaned['Room View(s)'] = value
                    elif label == "Room Code" and value:
                        # Use this if we don't already have room_code
                        if not cleaned.get('room_code'):
                            cleaned['room_code'] = value
                    # Could add more overview fields here as needed
        
        return cleaned
    
    def update_resort(self, resort_code: str) -> bool:
        """Update room data for a specific resort. Returns True if successful."""
        print(f"\n🔄 Updating rooms for {resort_code}...")
        
        # Load existing data
        all_data = self.load_existing_data()
        
        # Extract new room data
        rooms = self.extract_rooms_from_rsc(resort_code)
        
        if rooms:
            # Update the data for this resort
            all_data[resort_code] = rooms
            self.save_data(all_data)
            print(f"✅ Updated {len(rooms)} rooms for {resort_code}")
            return True
        else:
            print(f"⚠️  No rooms found for {resort_code}")
            return False
    
    def update_all_resorts(self):
        """Update room data for all resorts"""
        from tools.rsc_base import RESORT_CODES
        
        print("🚀 Updating rooms for all resorts...")
        
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
        
        print(f"\n🎉 Room update complete!")
        print(f"✅ Successful: {successful} resorts")
        print(f"❌ Failed: {failed} resorts")

def main():
    """Main function for command line usage"""
    import sys
    # Set up a path relative to cwd as data/rooms.json
    data_path = Path.cwd() / "data" / "rooms.json"
    updater = RoomUpdater(data_path)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_rooms.py <resort_code>  # Update specific resort")
        print("  python update_rooms.py all           # Update all resorts")
        print("\nExamples:")
        print("  python update_rooms.py BTC")
        print("  python update_rooms.py SRB")
        print("  python update_rooms.py all")
        return
    
    if sys.argv[1].lower() == 'all':
        updater.update_all_resorts()
    else:
        resort_code = sys.argv[1].upper()
        updater.update_resort(resort_code)

if __name__ == "__main__":
    main()
