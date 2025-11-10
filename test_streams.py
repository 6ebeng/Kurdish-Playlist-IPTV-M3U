#!/usr/bin/env python3
"""
M3U Stream Tester
Tests all URLs in an M3U playlist file to check if they're working
"""

import re
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import argparse
from datetime import datetime

class StreamTester:
    def __init__(self, timeout=10, max_workers=10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.results = {
            'working': [],
            'failed': [],
            'invalid': []
        }
    
    def parse_m3u(self, file_path):
        """Parse M3U file and extract channel info and URLs"""
        channels = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading file: {e}")
            return channels
        
        current_channel = {}
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and M3U header
            if not line or line == '#EXTM3U':
                continue
            
            # Parse channel info
            if line.startswith('#EXTINF:'):
                # Extract channel name
                match = re.search(r'tvg-name="([^"]*)"', line)
                channel_name = match.group(1) if match else "Unknown"
                
                # Extract group title
                match = re.search(r'group-title="([^"]*)"', line)
                group_title = match.group(1) if match else "Unknown"
                
                current_channel = {
                    'name': channel_name,
                    'group': group_title,
                    'line': i
                }
            
            # URL line
            elif line.startswith('http') or line.startswith('rtmp'):
                if current_channel:
                    current_channel['url'] = line
                    current_channel['url_line'] = i
                    channels.append(current_channel.copy())
                    current_channel = {}
                else:
                    # URL without channel info
                    channels.append({
                        'name': 'Unknown',
                        'group': 'Unknown',
                        'url': line,
                        'line': i,
                        'url_line': i
                    })
        
        return channels
    
    def test_url(self, channel):
        """Test if a stream URL is accessible"""
        url = channel['url']
        
        # Check if URL is malformed
        if url.startswith("https'://https://") or url.startswith("httpsG://"):
            return {
                **channel,
                'status': 'invalid',
                'error': 'Malformed URL (duplicate protocol or typo)',
                'status_code': None
            }
        
        # Basic URL validation
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {
                **channel,
                'status': 'invalid',
                'error': 'Invalid URL format',
                'status_code': None
            }
        
        # Test the URL
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.head(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code < 400:
                return {
                    **channel,
                    'status': 'working',
                    'status_code': response.status_code,
                    'error': None
                }
            else:
                # Try GET if HEAD fails
                response = requests.get(url, headers=headers, timeout=self.timeout, stream=True, allow_redirects=True)
                if response.status_code < 400:
                    return {
                        **channel,
                        'status': 'working',
                        'status_code': response.status_code,
                        'error': None
                    }
                else:
                    return {
                        **channel,
                        'status': 'failed',
                        'status_code': response.status_code,
                        'error': f'HTTP {response.status_code}'
                    }
                
        except requests.exceptions.Timeout:
            return {
                **channel,
                'status': 'failed',
                'status_code': None,
                'error': 'Timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                **channel,
                'status': 'failed',
                'status_code': None,
                'error': 'Connection Error'
            }
        except Exception as e:
            return {
                **channel,
                'status': 'failed',
                'status_code': None,
                'error': str(e)[:100]
            }
    
    def test_streams(self, channels, verbose=True):
        """Test all streams concurrently"""
        total = len(channels)
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"Testing {total} streams...")
            print(f"{'='*80}\n")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.test_url, channel): channel for channel in channels}
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                completed += 1
                
                if result['status'] == 'working':
                    self.results['working'].append(result)
                    if verbose:
                        print(f"✓ [{completed}/{total}] {result['name'][:40]:40} | Line {result['url_line']:4} | OK ({result['status_code']})")
                elif result['status'] == 'invalid':
                    self.results['invalid'].append(result)
                    if verbose:
                        print(f"⚠ [{completed}/{total}] {result['name'][:40]:40} | Line {result['url_line']:4} | INVALID: {result['error']}")
                else:
                    self.results['failed'].append(result)
                    if verbose:
                        print(f"✗ [{completed}/{total}] {result['name'][:40]:40} | Line {result['url_line']:4} | FAILED: {result['error']}")
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results['working']) + len(self.results['failed']) + len(self.results['invalid'])
        
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Total Streams:   {total}")
        print(f"✓ Working:       {len(self.results['working'])} ({len(self.results['working'])/total*100:.1f}%)")
        print(f"✗ Failed:        {len(self.results['failed'])} ({len(self.results['failed'])/total*100:.1f}%)")
        print(f"⚠ Invalid URLs:  {len(self.results['invalid'])} ({len(self.results['invalid'])/total*100:.1f}%)")
        print(f"{'='*80}\n")
    
    def save_report(self, output_file):
        """Save detailed report to file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"M3U Stream Test Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*100}\n\n")
            
            # Working streams
            f.write(f"WORKING STREAMS ({len(self.results['working'])})\n")
            f.write(f"{'-'*100}\n")
            for item in sorted(self.results['working'], key=lambda x: x['name']):
                f.write(f"✓ {item['name']}\n")
                f.write(f"  Group: {item['group']}\n")
                f.write(f"  Line: {item['url_line']}\n")
                f.write(f"  Status: {item['status_code']}\n")
                f.write(f"  URL: {item['url']}\n\n")
            
            # Failed streams
            f.write(f"\nFAILED STREAMS ({len(self.results['failed'])})\n")
            f.write(f"{'-'*100}\n")
            for item in sorted(self.results['failed'], key=lambda x: x['name']):
                f.write(f"✗ {item['name']}\n")
                f.write(f"  Group: {item['group']}\n")
                f.write(f"  Line: {item['url_line']}\n")
                f.write(f"  Error: {item['error']}\n")
                f.write(f"  URL: {item['url']}\n\n")
            
            # Invalid URLs
            f.write(f"\nINVALID URLs ({len(self.results['invalid'])})\n")
            f.write(f"{'-'*100}\n")
            for item in sorted(self.results['invalid'], key=lambda x: x['name']):
                f.write(f"⚠ {item['name']}\n")
                f.write(f"  Group: {item['group']}\n")
                f.write(f"  Line: {item['url_line']}\n")
                f.write(f"  Error: {item['error']}\n")
                f.write(f"  URL: {item['url']}\n\n")
        
        print(f"Detailed report saved to: {output_file}")
    
    def save_m3u_files(self, original_file, working_file=None, notworking_file=None):
        """
        Save working and not working streams to separate M3U files
        Also updates the original file to remove failed/invalid streams
        """
        import os
        
        # Read original M3U file to preserve all metadata
        try:
            with open(original_file, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
        except Exception as e:
            print(f"Error reading original file: {e}")
            return
        
        # Default filenames if not provided
        if working_file is None:
            base_name = os.path.splitext(original_file)[0]
            working_file = f"{base_name}_working.m3u"
        
        if notworking_file is None:
            base_name = os.path.splitext(original_file)[0]
            notworking_file = f"{base_name}_notworking.m3u"
        
        # Create sets of line numbers for quick lookup
        working_lines = {item['url_line'] for item in self.results['working']}
        failed_lines = {item['url_line'] for item in self.results['failed']}
        invalid_lines = {item['url_line'] for item in self.results['invalid']}
        notworking_lines = failed_lines | invalid_lines
        
        # Also track the EXTINF lines (usually 1 line before URL)
        working_extinf_lines = {item['line'] for item in self.results['working'] if 'line' in item}
        notworking_extinf_lines = {item['line'] for item in (self.results['failed'] + self.results['invalid']) if 'line' in item}
        
        # Write working streams
        with open(working_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            skip_next = False
            
            for i, line in enumerate(original_lines, 1):
                line_stripped = line.strip()
                
                # Skip M3U header from original
                if i == 1 and line_stripped == '#EXTM3U':
                    continue
                
                # Check if this is an EXTINF line for a working stream
                if line_stripped.startswith('#EXTINF:'):
                    if i in working_extinf_lines:
                        f.write(line)
                        skip_next = False
                    else:
                        skip_next = True
                # Check if this is a URL line
                elif line_stripped.startswith('http') or line_stripped.startswith('rtmp'):
                    if i in working_lines and not skip_next:
                        f.write(line)
                    skip_next = False
                # Other lines (comments, etc.)
                elif not skip_next and i-1 in working_lines:
                    f.write(line)
        
        print(f"✓ Working streams saved to: {working_file} ({len(self.results['working'])} streams)")
        
        # Write not working streams (failed + invalid)
        with open(notworking_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# Not Working Streams - Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'# Total: {len(self.results["failed"]) + len(self.results["invalid"])} streams\n')
            f.write(f'# Failed: {len(self.results["failed"])} | Invalid URLs: {len(self.results["invalid"])}\n\n')
            
            # Write failed streams
            if self.results['failed']:
                f.write('# ========== FAILED STREAMS (Connection/Timeout Issues) ==========\n\n')
                for item in sorted(self.results['failed'], key=lambda x: x['name']):
                    f.write(f'#EXTINF:-1 tvg-name="{item["name"]}" group-title="{item["group"]}",{item["name"]}\n')
                    f.write(f'# ERROR: {item["error"]} | Original Line: {item["url_line"]}\n')
                    f.write(f'{item["url"]}\n\n')
            
            # Write invalid URLs
            if self.results['invalid']:
                f.write('# ========== INVALID URLs (Malformed/Broken URLs) ==========\n\n')
                for item in sorted(self.results['invalid'], key=lambda x: x['name']):
                    f.write(f'#EXTINF:-1 tvg-name="{item["name"]}" group-title="{item["group"]}",{item["name"]}\n')
                    f.write(f'# ERROR: {item["error"]} | Original Line: {item["url_line"]}\n')
                    f.write(f'{item["url"]}\n\n')
        
        print(f"✗ Not working streams saved to: {notworking_file} ({len(self.results['failed']) + len(self.results['invalid'])} streams)")
    
    def update_original_file(self, original_file, backup=True):
        """
        Update the original M3U file to remove failed and invalid streams
        Creates a backup first
        """
        import os
        import shutil
        
        # Create backup
        if backup:
            backup_file = f"{original_file}.backup"
            try:
                shutil.copy2(original_file, backup_file)
                print(f"📋 Backup created: {backup_file}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
                return
        
        # Read original file
        try:
            with open(original_file, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
        except Exception as e:
            print(f"Error reading original file: {e}")
            return
        
        # Get line numbers to remove
        failed_lines = {item['url_line'] for item in self.results['failed']}
        invalid_lines = {item['url_line'] for item in self.results['invalid']}
        remove_lines = failed_lines | invalid_lines
        
        # Also remove corresponding EXTINF lines
        remove_extinf_lines = {item['line'] for item in (self.results['failed'] + self.results['invalid']) if 'line' in item}
        
        all_remove_lines = remove_lines | remove_extinf_lines
        
        # Write updated file
        with open(original_file, 'w', encoding='utf-8') as f:
            for i, line in enumerate(original_lines, 1):
                if i not in all_remove_lines:
                    f.write(line)
        
        removed_count = len(self.results['failed']) + len(self.results['invalid'])
        print(f"🔄 Original file updated: {original_file} (removed {removed_count} not working streams)")


def main():
    parser = argparse.ArgumentParser(description='Test M3U playlist stream URLs and organize working/not working streams')
    parser.add_argument('file', help='Path to M3U file')
    parser.add_argument('-t', '--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('-w', '--workers', type=int, default=10, help='Number of concurrent workers (default: 10)')
    parser.add_argument('-o', '--output', help='Save detailed report to file')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode - only show summary')
    parser.add_argument('--split', action='store_true', help='Split streams into working and notworking M3U files')
    parser.add_argument('--update-original', action='store_true', help='Update original file to remove failed streams (creates backup)')
    parser.add_argument('--no-backup', action='store_true', help='Skip backup when updating original file')
    parser.add_argument('--working-file', help='Custom name for working streams file (default: [original]_working.m3u)')
    parser.add_argument('--notworking-file', help='Custom name for not working streams file (default: [original]_notworking.m3u)')
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = StreamTester(timeout=args.timeout, max_workers=args.workers)
    
    # Parse M3U file
    print(f"Parsing M3U file: {args.file}")
    channels = tester.parse_m3u(args.file)
    
    if not channels:
        print("No channels found in the M3U file!")
        sys.exit(1)
    
    # Test streams
    tester.test_streams(channels, verbose=not args.quiet)
    
    # Print summary
    tester.print_summary()
    
    # Save report if requested
    if args.output:
        tester.save_report(args.output)
    
    # Split into separate files if requested
    if args.split:
        print(f"\n{'='*80}")
        print("Splitting streams into separate files...")
        print(f"{'='*80}\n")
        tester.save_m3u_files(args.file, args.working_file, args.notworking_file)
    
    # Update original file if requested
    if args.update_original:
        print(f"\n{'='*80}")
        print("Updating original file...")
        print(f"{'='*80}\n")
        tester.update_original_file(args.file, backup=not args.no_backup)
    
    # Always save to notworking files by default (even without --split flag)
    if not args.split and (len(tester.results['failed']) > 0 or len(tester.results['invalid']) > 0):
        print(f"\n{'='*80}")
        print("Saving not working streams...")
        print(f"{'='*80}\n")
        import os
        base_name = os.path.splitext(args.file)[0]
        notworking_file = args.notworking_file or f"{base_name}_notworking.m3u"
        
        # Just save the notworking file
        with open(notworking_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# Not Working Streams - Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'# Total: {len(tester.results["failed"]) + len(tester.results["invalid"])} streams\n')
            f.write(f'# Failed: {len(tester.results["failed"])} | Invalid URLs: {len(tester.results["invalid"])}\n\n')
            
            if tester.results['failed']:
                f.write('# ========== FAILED STREAMS (Connection/Timeout Issues) ==========\n\n')
                for item in sorted(tester.results['failed'], key=lambda x: x['name']):
                    f.write(f'#EXTINF:-1 tvg-name="{item["name"]}" group-title="{item["group"]}",{item["name"]}\n')
                    f.write(f'# ERROR: {item["error"]} | Original Line: {item["url_line"]}\n')
                    f.write(f'{item["url"]}\n\n')
            
            if tester.results['invalid']:
                f.write('# ========== INVALID URLs (Malformed/Broken URLs) ==========\n\n')
                for item in sorted(tester.results['invalid'], key=lambda x: x['name']):
                    f.write(f'#EXTINF:-1 tvg-name="{item["name"]}" group-title="{item["group"]}",{item["name"]}\n')
                    f.write(f'# ERROR: {item["error"]} | Original Line: {item["url_line"]}\n')
                    f.write(f'{item["url"]}\n\n')
        
        print(f"✗ Not working streams saved to: {notworking_file} ({len(tester.results['failed']) + len(tester.results['invalid'])} streams)")
    
    print()  # Empty line for cleaner output


if __name__ == '__main__':
    main()
