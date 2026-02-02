"""
Quick Fix Script
Memperbaiki masalah umum dengan cepat
"""
import subprocess
import sys
import os


def print_header(text):
    """Print header dengan style"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.7+)")
        return False


def check_pip():
    """Check pip installation"""
    print("\nChecking pip...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ pip installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ pip not found")
            return False
    except:
        print("✗ pip error")
        return False


def upgrade_pip():
    """Upgrade pip"""
    print("\nUpgrading pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                      check=True)
        print("✓ pip upgraded successfully")
        return True
    except:
        print("✗ Failed to upgrade pip")
        return False


def install_dependencies():
    """Install/upgrade all dependencies"""
    print("\nInstalling/upgrading dependencies...")
    
    packages = [
        'PyQt5',
        'yt-dlp',
        'gallery-dl',
        'pytube',
        'you-get',
        'mutagen'
    ]
    
    success_count = 0
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', package],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"✓ {package} installed/upgraded successfully")
                success_count += 1
            else:
                print(f"✗ {package} installation failed")
                print(f"   Error: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print(f"✗ {package} installation timeout")
        except Exception as e:
            print(f"✗ {package} error: {str(e)[:100]}")
    
    print(f"\n{success_count}/{len(packages)} packages installed successfully")
    return success_count == len(packages)


def check_ffmpeg():
    """Check FFmpeg installation"""
    print("\nChecking FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg installed: {version_line}")
            return True
        else:
            print("✗ FFmpeg not found")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not found in PATH")
        print("\nPlease install FFmpeg:")
        print("  Windows: https://ffmpeg.org/download.html")
        print("  Linux: sudo apt install ffmpeg")
        print("  Mac: brew install ffmpeg")
        return False
    except:
        print("✗ FFmpeg check error")
        return False


def fix_pytube():
    """Fix pytube installation specifically"""
    print("\nFixing pytube...")
    try:
        # Uninstall old version
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'pytube', '-y'],
                      capture_output=True)
        
        # Install latest version
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pytube'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ pytube installed successfully")
            
            # Verify import
            try:
                import pytube
                print(f"✓ pytube import successful (version: {pytube.__version__})")
                return True
            except ImportError as e:
                print(f"✗ pytube import failed: {e}")
                print("  Note: pytube is optional, app will work without it")
                return False
        else:
            print("✗ pytube installation failed")
            print("  Note: pytube is optional, app will work without it")
            return False
    except Exception as e:
        print(f"✗ pytube fix error: {str(e)[:100]}")
        print("  Note: pytube is optional, app will work without it")
        return False


def clear_cache():
    """Clear cache folders"""
    print("\nClearing cache...")
    
    cache_folders = [
        os.path.expanduser('~/.cache/yt-dlp'),
        os.path.expanduser('~/.cache/gallery-dl'),
    ]
    
    cleared = 0
    for folder in cache_folders:
        if os.path.exists(folder):
            try:
                import shutil
                shutil.rmtree(folder)
                print(f"✓ Cleared {folder}")
                cleared += 1
            except Exception as e:
                print(f"✗ Failed to clear {folder}: {str(e)[:50]}")
        else:
            print(f"  {folder} doesn't exist (OK)")
    
    print(f"\n{cleared} cache folders cleared")
    return True


def test_imports():
    """Test importing all modules"""
    print("\nTesting module imports...")
    
    modules = {
        'PyQt5': 'PyQt5.QtWidgets',
        'yt-dlp': 'yt_dlp',
        'gallery-dl': 'gallery_dl',
        'pytube': 'pytube',
        'you-get': 'you_get',
        'mutagen': 'mutagen'
    }
    
    success_count = 0
    
    for name, module in modules.items():
        try:
            __import__(module)
            print(f"✓ {name:15} : Import OK")
            success_count += 1
        except ImportError as e:
            if name == 'pytube':
                print(f"⚠ {name:15} : Not available (optional)")
            else:
                print(f"✗ {name:15} : Import failed - {str(e)[:40]}")
    
    print(f"\n{success_count}/{len(modules)} modules imported successfully")
    return success_count >= len(modules) - 1  # -1 karena pytube optional


def update_ytdlp():
    """Update yt-dlp to latest version"""
    print("\nUpdating yt-dlp to latest version...")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ yt-dlp updated successfully")
            
            # Check version
            import yt_dlp
            print(f"  Version: {yt_dlp.version.__version__}")
            return True
        else:
            print("✗ yt-dlp update failed")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}")
        return False


def main():
    """Main fix routine"""
    print_header("Media Downloader - Quick Fix Tool")
    
    print("This script will:")
    print("  1. Check system requirements")
    print("  2. Fix dependency issues")
    print("  3. Clear cache")
    print("  4. Update critical packages")
    print()
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Step 1: Check Python
    print_header("Step 1: Checking Python")
    if not check_python_version():
        print("\n❌ Please upgrade Python to 3.7 or higher")
        return
    
    # Step 2: Check pip
    print_header("Step 2: Checking pip")
    if not check_pip():
        print("\n❌ Please install pip")
        return
    
    # Step 3: Upgrade pip
    print_header("Step 3: Upgrading pip")
    upgrade_pip()
    
    # Step 4: Install dependencies
    print_header("Step 4: Installing Dependencies")
    install_dependencies()
    
    # Step 5: Fix pytube specifically
    print_header("Step 5: Fixing pytube")
    fix_pytube()
    
    # Step 6: Update yt-dlp
    print_header("Step 6: Updating yt-dlp")
    update_ytdlp()
    
    # Step 7: Check FFmpeg
    print_header("Step 7: Checking FFmpeg")
    check_ffmpeg()
    
    # Step 8: Clear cache
    print_header("Step 8: Clearing Cache")
    clear_cache()
    
    # Step 9: Test imports
    print_header("Step 9: Testing Imports")
    imports_ok = test_imports()
    
    # Summary
    print_header("Summary")
    
    if imports_ok:
        print("✅ All critical components are working!")
        print("\nYou can now run the application:")
        print("  python main.py")
        print("\nOr use the run script:")
        print("  Windows: run.bat")
        print("  Linux/Mac: ./run.sh")
    else:
        print("⚠️  Some components have issues")
        print("\nPlease check TROUBLESHOOTING.md for more help")
        print("\nThe app may still work with limited functionality")
    
    print("\n" + "=" * 60)
    print("\nPress Enter to exit...")
    input()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("\nPlease report this error if it persists")
        input("\nPress Enter to exit...")