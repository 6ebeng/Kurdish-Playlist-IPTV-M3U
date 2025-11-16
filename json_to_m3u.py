#!/usr/bin/env python3
"""
JSON to M3U Converter
Parses JSON files from json folder and converts them to M3U playlist format
Automatically removes duplicates based on URL
"""

import json
import os
import glob
from datetime import datetime

class JSONToM3U:
    def __init__(self, json_folder='json', output_file='from_json.m3u'):
        self.json_folder = json_folder
        self.output_file = output_file
        self.channels = []
        self.seen_urls = set()  # Track URLs to avoid duplicates
        self.seen_names = {}    # Track channel names and their URLs
        self.duplicates_removed = 0
        
    def parse_json_files(self):
        """Parse all JSON files in the json folder"""
        json_files = glob.glob(os.path.join(self.json_folder, '*.json'))
        
        if not json_files:
            print(f"No JSON files found in '{self.json_folder}' folder!")
            return False
        
        print(f"Found {len(json_files)} JSON files to process...")
        
        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Extract result array
                if 'result' in data and isinstance(data['result'], list):
                    self.process_channels(data['result'], json_file)
                else:
                    print(f"⚠ Skipping {os.path.basename(json_file)} - no 'result' array found")
                    
            except Exception as e:
                print(f"✗ Error reading {os.path.basename(json_file)}: {e}")
        
        return True
    
    def process_channels(self, channels, source_file):
        """Process channels from a JSON result array"""
        for channel in channels:
            try:
                # Extract channel information
                name = channel.get('name', 'Unknown')
                title = channel.get('title', name)
                href = channel.get('href', '')
                pict = channel.get('pict', '')
                epg_id = channel.get('epg_id', 0)
                
                # Skip if no URL
                if not href:
                    continue
                
                # Check for duplicate URL
                if href in self.seen_urls:
                    self.duplicates_removed += 1
                    print(f"  ⊗ Duplicate URL skipped: {name} ({href[:50]}...)")
                    continue
                
                # Check for duplicate name with different URL
                if name in self.seen_names:
                    old_url = self.seen_names[name]
                    if old_url != href:
                        print(f"  ⚠ Same name, different URL: {name}")
                        print(f"    Old: {old_url[:60]}...")
                        print(f"    New: {href[:60]}...")
                        # Keep the first one, skip the duplicate name
                        self.duplicates_removed += 1
                        continue
                
                # Add to seen URLs and names
                self.seen_urls.add(href)
                self.seen_names[name] = href
                
                # Determine group title
                group_title = "General"
                
                # Try to categorize based on name
                name_lower = name.lower()
                if any(x in name_lower for x in ['sport', 'bein', 'ssc', 'kass', 'رياضية', 'الرياضية']):
                    group_title = "Sports"
                elif any(x in name_lower for x in ['mbc', 'osn', 'movie', 'film', 'أكشن', 'دراما']):
                    group_title = "Entertainment"
                elif any(x in name_lower for x in ['news', 'الشرقية', 'العراقية', 'السومرية', 'اخبار', 'نيوز']):
                    group_title = "News"
                
                # Add channel
                channel_info = {
                    'name': name,
                    'title': title,
                    'url': href,
                    'group': group_title,
                    'logo': pict,
                    'epg_id': epg_id
                }
                
                self.channels.append(channel_info)
                
            except Exception as e:
                print(f"  ✗ Error processing channel: {e}")
    
    def save_m3u(self):
        """Save channels to M3U file"""
        if not self.channels:
            print("No channels to save!")
            return False
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                # Write M3U header
                f.write('#EXTM3U\n')
                f.write(f'# Generated from JSON files - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write(f'# Total Channels: {len(self.channels)}\n')
                f.write(f'# Duplicates Removed: {self.duplicates_removed}\n\n')
                
                # Group channels by category
                sports = [ch for ch in self.channels if ch['group'] == 'Sports']
                entertainment = [ch for ch in self.channels if ch['group'] == 'Entertainment']
                news = [ch for ch in self.channels if ch['group'] == 'News']
                general = [ch for ch in self.channels if ch['group'] == 'General']
                
                # Write channels by group
                if sports:
                    f.write('# ========== Sports Channels ==========\n\n')
                    self.write_channels(f, sports)
                
                if entertainment:
                    f.write('# ========== Entertainment Channels ==========\n\n')
                    self.write_channels(f, entertainment)
                
                if news:
                    f.write('# ========== News Channels ==========\n\n')
                    self.write_channels(f, news)
                
                if general:
                    f.write('# ========== General Channels ==========\n\n')
                    self.write_channels(f, general)
            
            return True
            
        except Exception as e:
            print(f"Error saving M3U file: {e}")
            return False
    
    def write_channels(self, file, channels):
        """Write a list of channels to file"""
        for i, channel in enumerate(channels, 1):
            # Build EXTINF line
            extinf = f'#EXTINF:-1'
            
            # Add tvg-id if available
            if channel['epg_id'] and channel['epg_id'] != 0:
                extinf += f' tvg-id="{channel["epg_id"]}"'
            
            # Add tvg-name
            extinf += f' tvg-name="{channel["name"]}"'
            
            # Add tvg-logo if available
            if channel['logo']:
                extinf += f' tvg-logo="{channel["logo"]}"'
            
            # Add group-title
            extinf += f' group-title="{channel["group"]}"'
            
            # Add channel name at the end
            extinf += f',{channel["title"]}'
            
            # Write EXTINF and URL
            file.write(f'{extinf}\n')
            file.write(f'{channel["url"]}\n')
    
    def print_summary(self):
        """Print conversion summary"""
        print(f"\n{'='*80}")
        print("CONVERSION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Channels Added:     {len(self.channels)}")
        print(f"Duplicates Removed:       {self.duplicates_removed}")
        
        # Count by category
        sports = sum(1 for ch in self.channels if ch['group'] == 'Sports')
        entertainment = sum(1 for ch in self.channels if ch['group'] == 'Entertainment')
        news = sum(1 for ch in self.channels if ch['group'] == 'News')
        general = sum(1 for ch in self.channels if ch['group'] == 'General')
        
        print(f"\nBy Category:")
        print(f"  Sports:          {sports}")
        print(f"  Entertainment:   {entertainment}")
        print(f"  News:            {news}")
        print(f"  General:         {general}")
        print(f"{'='*80}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert JSON files to M3U playlist format')
    parser.add_argument('--json-folder', default='json', help='Folder containing JSON files (default: json)')
    parser.add_argument('--output', '-o', default='from_json.m3u', help='Output M3U file (default: from_json.m3u)')
    parser.add_argument('--no-test', action='store_true', help='Skip testing the created M3U file')
    parser.add_argument('--timeout', '-t', type=int, default=8, help='Test timeout in seconds (default: 8)')
    parser.add_argument('--workers', '-w', type=int, default=15, help='Number of test workers (default: 15)')
    
    args = parser.parse_args()
    
    # Create converter
    converter = JSONToM3U(json_folder=args.json_folder, output_file=args.output)
    
    # Parse JSON files
    print(f"{'='*80}")
    print("JSON TO M3U CONVERTER")
    print(f"{'='*80}\n")
    
    if not converter.parse_json_files():
        return 1
    
    # Save M3U file
    print(f"\nSaving to M3U file: {args.output}")
    if not converter.save_m3u():
        return 1
    
    print(f"✓ M3U file created successfully: {args.output}")
    
    # Print summary
    converter.print_summary()
    
    # Test by default (unless --no-test is specified)
    if not args.no_test:
        print(f"{'='*80}")
        print("TESTING AND CLEANING M3U FILE")
        print(f"{'='*80}\n")
        
        import subprocess
        import sys
        
        # Run test_streams.py with --update-original to remove broken channels
        cmd = [
            sys.executable,
            'test_streams.py',
            args.output,
            '--update-original',
            '-t', str(args.timeout),
            '-w', str(args.workers)
        ]
        
        try:
            result = subprocess.run(cmd, check=False)
            return result.returncode
        except Exception as e:
            print(f"Error running tests: {e}")
            return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
