# M3U Stream Tester

A Python script to test all stream URLs in M3U playlist files and check if they're working.

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
python test_streams.py arabic.m3u
```

This will test all streams and create `arabic_notworking.m3u` with failed/broken links.

### Split into working and not working files:

```powershell
python test_streams.py arabic.m3u --split
```

Creates:

- `arabic_working.m3u` - Only working streams
- `arabic_notworking.m3u` - Failed and invalid streams

### Update original file (removes broken streams):

```powershell
python test_streams.py arabic.m3u --update-original
```

This creates a backup (`arabic.m3u.backup`) and removes all failed/invalid streams from the original file.

### Test with custom timeout (15 seconds):

```powershell
python test_streams.py arabic.m3u -t 15
```

### Save detailed report to file:

```powershell
python test_streams.py arabic.m3u -o report.txt
```

### Quiet mode (only show summary):

```powershell
python test_streams.py arabic.m3u -q
```

### Test Kurdish playlist:

```powershell
python test_streams.py kurdish.m3u
```

### Complete workflow (test, split, and save report):

```powershell
python test_streams.py arabic.m3u --split -o arabic_report.txt
```

### Custom output filenames:

```powershell
python test_streams.py arabic.m3u --split --working-file arabic_good.m3u --notworking-file arabic_bad.m3u
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
Testing 117 streams...
================================================================================

✓ [1/117] MBC 1                                     | Line    3 | OK (200)
✓ [2/117] MBC 2                                     | Line    5 | OK (200)
⚠ [3/117] Roya Kitchen                              | Line  161 | INVALID: Malformed URL (duplicate protocol or typo)
✗ [4/117] Some Channel                              | Line   10 | FAILED: Timeout

================================================================================
SUMMARY
================================================================================
Total Streams:   117
✓ Working:       95 (81.2%)
✗ Failed:        20 (17.1%)
⚠ Invalid URLs:  2 (1.7%)
================================================================================
```

## Issues Found in Your Playlist

The script detected some malformed URLs in your `arabic.m3u` file:

1. **Line 161** - Roya Kitchen: `https'://https://www.google.com/...` (duplicate protocol)
2. **Line 105** - Hawas: `httpsG://...` (typo in protocol)
3. **Line 95** - AL Itihad: Contains Google search URL instead of stream URL

These should be fixed for the streams to work properly.

## Tips

- Use a larger timeout (`-t 20`) if you have slow internet connection
- Increase workers (`-w 20`) for faster testing if you have good internet
- Save reports (`-o`) to track changes over time
- Some streams may require specific headers or authentication - the script uses basic HTTP requests

## License

Free to use and modify.
