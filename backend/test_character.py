#!/usr/bin/env python3
"""
Simple script to test character generation with nano-bannan model
"""
import requests
import json

def test_character_generation(sketch_path, character_name):
    """Test the character generation endpoint"""
    
    url = "http://localhost:8000/characters/"
    
    try:
        # Prepare the files and data
        with open(sketch_path, 'rb') as sketch_file:
            files = {
                'sketch': ('sketch.png', sketch_file, 'image/png')
            }
            data = {
                'name': character_name
            }
            
            print(f"🚀 Uploading sketch: {sketch_path}")
            print(f"📝 Character name: {character_name}")
            print("⏳ Generating character with nano-bannan model...")
            
            # Make the request
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                char_id = result['character_id']
                
                print("✅ Character created successfully!")
                print(f"🆔 Character ID: {char_id}")
                print(f"📸 View generated character: http://localhost:8000/characters/{char_id}/image/generated")
                print(f"🎨 View original sketch: http://localhost:8000/characters/{char_id}/image/sketch")
                
                return char_id
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return None
                
    except FileNotFoundError:
        print(f"❌ Sketch file not found: {sketch_path}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_all_characters():
    """List all generated characters"""
    url = "http://localhost:8000/characters/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            characters = result['characters']
            
            print(f"\n📋 Found {len(characters)} characters:")
            for char in characters:
                char_id = char['id']
                name = char['name']
                print(f"  • {name} (ID: {char_id})")
                print(f"    Generated: http://localhost:8000/characters/{char_id}/image/generated")
            
            return characters
        else:
            print(f"❌ Error listing characters: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

if __name__ == "__main__":
    print("🎮 Character Generation Test with nano-bannan model")
    print("=" * 50)
    
    # You can modify these values
    sketch_path = input("Enter path to your sketch file (or press Enter for example): ").strip()
    if not sketch_path:
        print("ℹ️  No sketch provided. Please provide a sketch file path.")
        exit()
    
    character_name = input("Enter character name (or press Enter for 'Test Character'): ").strip()
    if not character_name:
        character_name = "Test Character"
    
    # Test character generation
    char_id = test_character_generation(sketch_path, character_name)
    
    if char_id:
        print(f"\n🎉 Success! Open these URLs in your browser:")
        print(f"Original sketch: http://localhost:8000/characters/{char_id}/image/sketch")
        print(f"Generated character: http://localhost:8000/characters/{char_id}/image/generated")
    
    # Show all characters
    print("\n" + "=" * 50)
    list_all_characters()