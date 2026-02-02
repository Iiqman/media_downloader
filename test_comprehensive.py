"""
Comprehensive Test Script
Test setiap komponen step by step
"""
import sys
import traceback

def test_step(step_num, description, func):
    """Test satu step dengan error handling"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)
    try:
        result = func()
        print(f"✅ Step {step_num} PASSED")
        return True, result
    except Exception as e:
        print(f"❌ Step {step_num} FAILED: {e}")
        traceback.print_exc()
        return False, None

def step1_imports():
    """Test basic imports"""
    print("Testing imports...")
    from PyQt5.QtWidgets import QApplication
    print("  ✓ PyQt5.QtWidgets")
    from PyQt5.QtCore import Qt
    print("  ✓ PyQt5.QtCore")
    from PyQt5.QtGui import QPixmap
    print("  ✓ PyQt5.QtGui")
    return True

def step2_backend_imports():
    """Test backend imports"""
    print("Testing backend imports...")
    from backend import YouTubeDownloader
    print("  ✓ YouTubeDownloader")
    from backend import InstagramDownloader
    print("  ✓ InstagramDownloader")
    from backend import TikTokDownloader
    print("  ✓ TikTokDownloader")
    from backend import FacebookDownloader
    print("  ✓ FacebookDownloader")
    return True

def step3_utils_imports():
    """Test utils imports"""
    print("Testing utils imports...")
    from utils import ConfigManager
    print("  ✓ ConfigManager")
    from utils import HistoryManager
    print("  ✓ HistoryManager")
    return True

def step4_ui_imports():
    """Test UI imports"""
    print("Testing UI imports...")
    from ui.styles import get_theme
    print("  ✓ styles")
    from ui.settings_dialog import SettingsDialog
    print("  ✓ SettingsDialog")
    from ui.history_widget import HistoryWidget
    print("  ✓ HistoryWidget")
    from ui.platform_widget import PlatformWidget
    print("  ✓ PlatformWidget")
    from ui.main_window import MainWindow
    print("  ✓ MainWindow")
    return True

def step5_create_app():
    """Create QApplication"""
    from PyQt5.QtWidgets import QApplication
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    print("  ✓ QApplication created")
    return app

def step6_create_config():
    """Create ConfigManager"""
    from utils import ConfigManager
    print("Creating ConfigManager...")
    config = ConfigManager()
    print(f"  ✓ Config loaded: {config.config_file}")
    print(f"  Download folder: {config.get('download_folder')}")
    return config

def step7_create_platform_widget(app, config):
    """Create PlatformWidget"""
    from ui.platform_widget import PlatformWidget
    print("Creating PlatformWidget for YouTube...")
    widget = PlatformWidget("YouTube", config)
    print("  ✓ YouTube PlatformWidget created")
    widget.show()
    print("  ✓ Widget shown")
    return widget

def step8_create_main_window(app):
    """Create MainWindow"""
    from ui.main_window import MainWindow
    print("Creating MainWindow...")
    window = MainWindow()
    print("  ✓ MainWindow created")
    window.show()
    print("  ✓ MainWindow shown")
    return window

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     Media Downloader - Comprehensive Test Suite         ║
╚══════════════════════════════════════════════════════════╝
""")
    
    results = {}
    
    # Step 1: Basic imports
    success, _ = test_step(1, "Basic PyQt5 Imports", step1_imports)
    results['imports'] = success
    if not success:
        print("\n❌ FATAL: PyQt5 not installed properly")
        print("Fix: pip install PyQt5")
        return
    
    # Step 2: Backend imports
    success, _ = test_step(2, "Backend Imports", step2_backend_imports)
    results['backend'] = success
    if not success:
        print("\n❌ WARNING: Backend import issues")
        print("Fix: pip install yt-dlp gallery-dl")
    
    # Step 3: Utils imports
    success, _ = test_step(3, "Utils Imports", step3_utils_imports)
    results['utils'] = success
    if not success:
        print("\n❌ FATAL: Utils import failed")
        return
    
    # Step 4: UI imports
    success, _ = test_step(4, "UI Imports", step4_ui_imports)
    results['ui_imports'] = success
    if not success:
        print("\n❌ FATAL: UI import failed - check syntax errors")
        return
    
    # Step 5: Create QApplication
    success, app = test_step(5, "Create QApplication", step5_create_app)
    results['qapp'] = success
    if not success:
        print("\n❌ FATAL: Cannot create QApplication")
        return
    
    # Step 6: Create Config
    success, config = test_step(6, "Create ConfigManager", step6_create_config)
    results['config'] = success
    if not success:
        print("\n❌ FATAL: Config creation failed")
        return
    
    # Step 7: Create PlatformWidget
    success, widget = test_step(7, "Create PlatformWidget", 
                                lambda: step7_create_platform_widget(app, config))
    results['platform_widget'] = success
    if not success:
        print("\n❌ ERROR: PlatformWidget creation failed")
        print("This is where the crash likely occurs!")
    
    # Step 8: Create MainWindow
    success, window = test_step(8, "Create MainWindow", 
                                lambda: step8_create_main_window(app))
    results['main_window'] = success
    if not success:
        print("\n❌ ERROR: MainWindow creation failed")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test:20} : {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("\nApplication should work. Running main app...")
        print("(Close window to exit)")
        
        if window:
            sys.exit(app.exec_())
    else:
        print(f"\n❌ {total - passed} TESTS FAILED")
        print("\nCheck the failed steps above for specific errors.")
        print("\nCommon fixes:")
        print("  1. pip install -r requirements.txt")
        print("  2. python fix_issues.py")
        print("  3. Check TROUBLESHOOTING.md")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        traceback.print_exc()