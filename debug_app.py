"""
Debug Script - Test aplikasi startup
"""
import sys
import traceback

print("=" * 60)
print("Media Downloader - Debug Test")
print("=" * 60)

try:
    print("\n1. Testing imports...")
    from PyQt5.QtWidgets import QApplication
    print("   ✓ PyQt5 imported")
    
    from ui import MainWindow
    print("   ✓ MainWindow imported")
    
    print("\n2. Creating QApplication...")
    app = QApplication(sys.argv)
    print("   ✓ QApplication created")
    
    print("\n3. Creating MainWindow...")
    window = MainWindow()
    print("   ✓ MainWindow created")
    
    print("\n4. Showing window...")
    window.show()
    print("   ✓ Window shown")
    
    print("\n✅ All tests passed! Starting application...")
    print("   Press Ctrl+C to exit\n")
    
    sys.exit(app.exec_())
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nMissing dependencies. Please install:")
    print("   pip install -r requirements.txt")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Troubleshooting:")
    print("1. Check if all dependencies installed")
    print("2. Run: python test_dependencies.py")
    print("3. Run: python fix_issues.py")
    print("4. Check TROUBLESHOOTING.md")
    print("=" * 60)