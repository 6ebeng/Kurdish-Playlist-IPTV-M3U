# Kurdish-Playlist-IPTV-M3U

A Python script to test and manage M3U playlist files for Kurdish and Arabic IPTV streams. This tool helps you validate stream URLs, remove broken links, and maintain clean playlists.

## Features

- ✅ Tests all URLs in M3U playlist files
- ✅ Concurrent testing for faster results
- ✅ Detects malformed URLs (like the ones in your playlist)
- ✅ Colored output showing working/failed/invalid streams
- ✅ **Automatically moves failed/broken links to separate `_notworking.m3u` file**
- ✅ **Optionally splits working and not working streams into separate files**
- ✅ **Can update original file to remove broken streams (with backup)**
- ✅ Generates detailed reports
- ✅ Configurable timeout and worker threads
- ✅ Progress tracking

## Installation

1. Make sure you have Python 3.6+ installed
2. Install required dependencies:

```powershell
pip install requests
```

## Usage

### Basic usage (automatically saves not working streams):

```powershell
python test_streams.py Chennels.m3u
```

This will test all streams and create `Chennels_notworking.m3u` with failed/broken links.

### Split into working and not working files:

```powershell
python test_streams.py Chennels.m3u --split
```

Creates:

- `Chennels_working.m3u` - Only working streams
- `Chennels_notworking.m3u` - Failed and invalid streams

### Update original file (removes broken streams):

```powershell
python test_streams.py Chennels.m3u --update-original
```

This creates a backup (`Chennels.m3u.backup`) and removes all failed/invalid streams from the original file.

### Test with custom timeout and workers:

```powershell
python test_streams.py Chennels.m3u -t 8 -w 15
```

### Save detailed report to file:

```powershell
python test_streams.py Chennels.m3u -o report.txt
```

### Quiet mode (only show summary):

```powershell
python test_streams.py Chennels.m3u -q
```

### Test individual playlists:

```powershell
# Test Kurdish channels only
python test_streams.py kurdish.m3u

# Test Arabic channels only
python test_streams.py arabic.m3u

# Test combined playlist
python test_streams.py Chennels.m3u
```

### Complete workflow (test, update, and save report):

```powershell
python test_streams.py Chennels.m3u --update-original -t 8 -w 15 -o report.txt
```

### Custom output filenames:

```powershell
python test_streams.py Chennels.m3u --split --working-file channels_good.m3u --notworking-file channels_bad.m3u
```

## Command Line Options

- `file` - Path to the M3U file (required)
- `-t, --timeout` - Request timeout in seconds (default: 10)
- `-w, --workers` - Number of concurrent workers (default: 10)
- `-o, --output` - Save detailed report to specified file
- `-q, --quiet` - Quiet mode - only show summary
- `--split` - Split streams into separate working and notworking M3U files
- `--update-original` - Update original file to remove failed streams (creates backup)
- `--no-backup` - Skip backup when updating original file
- `--working-file` - Custom name for working streams file
- `--notworking-file` - Custom name for not working streams file

## Output

The script will show:

- ✓ Working streams (green checkmark)
- ✗ Failed streams (red X)
- ⚠ Invalid URLs (warning)

### Example output:

```
================================================================================
Testing 172 streams...
================================================================================

✓ [1/172] NRT Sport ᴴᴰ                             | Line   29 | OK (200)
✓ [2/172] Shna TV ᴴᴰ                               | Line   31 | OK (200)
✗ [43/172] Mihrab TV ᴴᴰ                            | Line   95 | FAILED: HTTP 404
✓ [100/172] Soz Quran ᴴᴰ                           | Line  201 | OK (200)

================================================================================
SUMMARY
================================================================================
Total Streams:   172
✓ Working:       157 (91.3%)
✗ Failed:        15 (8.7%)
⚠ Invalid URLs:  0 (0.0%)
================================================================================
```

## Playlist Files

This repository contains the following playlists:

- **Chennels.m3u** - Combined playlist with Kurdish (104 channels) and Arabic (69 channels) streams
- **kurdish.m3u** - Kurdish channels only (104 channels)
- **arabic.m3u** - Arabic channels only (68 working channels)

All playlists are regularly tested and cleaned to ensure stream quality.

## Tips

- Use a larger timeout (`-t 20`) if you have slow internet connection
- Increase workers (`-w 20`) for faster testing if you have good internet
- Save reports (`-o`) to track changes over time
- Some streams may require specific headers or authentication - the script uses basic HTTP requests

## License

Free to use and modify.
