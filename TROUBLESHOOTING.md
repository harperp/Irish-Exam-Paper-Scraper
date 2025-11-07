# Troubleshooting Guide

## Connection Errors

### Problem: "Connection refused" or "Max retries exceeded"

```
✗ Error downloading file.pdf: HTTPSConnectionPool... Max retries exceeded
✗ Connection failed after 3 attempts: file.pdf
```

**Cause:** The examinations.ie website is rate-limiting or blocking your requests when downloading too many files too quickly.

**Solutions:**

1. **Wait and retry** - The script automatically retries failed downloads 3 times with increasing delays
2. **Files are skipped** - Already downloaded files won't be re-downloaded, so just run the script again
3. **The script will resume** - Simply re-run the same command and it will pick up where it left off

**Example:**
```bash
# First run - downloads some files, gets connection errors
python3 download_exams_v2.py --cert lc --subject history --year-range 2000-2024

# Just run again - will skip already downloaded files and continue
python3 download_exams_v2.py --cert lc --subject history --year-range 2000-2024
```

### Built-in Protections

The script includes several features to avoid rate limiting:

- ✅ **Automatic retries**: 3 attempts per file with exponential backoff
- ✅ **Delays between downloads**: 2 seconds between each file
- ✅ **Delays between years**: 5 seconds when downloading multiple years
- ✅ **Skip existing files**: Won't re-download files that already exist

### Tips

1. **Download in smaller batches**
   ```bash
   # Instead of all years at once:
   python3 download_exams_v2.py --cert lc --subject mathematics

   # Try smaller ranges:
   python3 download_exams_v2.py --cert lc --subject mathematics --year-range 2020-2024
   python3 download_exams_v2.py --cert lc --subject mathematics --year-range 2015-2019
   python3 download_exams_v2.py --cert lc --subject mathematics --year-range 2010-2014
   ```

2. **Download during off-peak hours**
   - Late evening or early morning may have fewer rate limits

3. **Check your internet connection**
   ```bash
   # Test connection to the website
   curl -I https://www.examinations.ie
   ```

## ChromeDriver Issues

### Problem: "chromedriver not found" or version mismatch

**Solution:**
```bash
# Re-run the setup script
./setup_chromedriver_local.sh
```

### Problem: Browser window opens but nothing happens

**Cause:** Page taking too long to load

**Solution:** The script has built-in waits, but if your connection is slow, you may need to increase them manually in the code.

## No PDFs Found

### Problem: "No PDF links found"

**Possible causes:**

1. **Subject not available for that year**
   ```bash
   # Check what's available
   python3 check_available_years.py --cert jc --subject history
   ```

2. **Wrong certificate level**
   - Junior Cert uses `jc` not `junior`
   - Leaving Cert uses `lc` not `leaving`

3. **Subject name doesn't match**
   ```bash
   # List all subjects for a year
   python3 download_all_subjects.py --year 2024 --level lc --list-subjects
   ```

## Import Errors

### Problem: "ModuleNotFoundError: No module named 'selenium'"

**Solution:**
```bash
# Reinstall dependencies
pip3 install --user -r requirements.txt
```

## File Permission Errors

### Problem: "Permission denied" when creating directories

**Solution:**
```bash
# Use a different output directory where you have permissions
python3 download_exams_v2.py --cert lc --subject mathematics --output ~/Documents/exams
```

## Getting Help

If you encounter other issues:

1. **Check the logs** - The script prints detailed error messages
2. **Verify the website is up** - Visit https://www.examinations.ie/exammaterialarchive/
3. **Check your Python version** - Requires Python 3.7+
   ```bash
   python3 --version
   ```

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `Connection refused` | Website blocking/rate limiting | Wait and retry |
| `No such element` | Page structure changed | Website may have updated |
| `TimeoutException` | Page took too long to load | Check internet connection |
| `FileNotFoundError: chromedriver` | ChromeDriver not installed | Run `./setup_chromedriver_local.sh` |

## Still Having Issues?

Open an issue on GitHub with:
- The full error message
- The command you ran
- Your Python version (`python3 --version`)
- Your OS (macOS, Linux, Windows)
