"""
Freeze Diagnostic - Diagnose app freeze issues
"""
import sys
import time

def test_step_by_step():
    """Test step by step dengan delays"""
    print("Step-by-step test")
    print("="*60)
    
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    print("Step 1: QApplication.setAttribute...")
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    time.sleep(0.5)
    print("  OK")
    
    print("\nStep 2: QApplication()")
    app = QApplication(sys.argv)
    time.sleep(0.5)
    print("  OK")
    
    print("\nStep 3: Import MainWindow")
    from ui import MainWindow
    time.sleep(0.5)
    print("  OK")
    
    print("\nStep 4: MainWindow()")
    start = time.time()
    window = MainWindow()
    elapsed = time.time() - start
    print(f"  OK (took {elapsed:.2f}s)")
    
    print("\nStep 5: window.show()")
    start = time.time()
    window.show()
    elapsed = time.time() - start
    print(f"  OK (took {elapsed:.2f}s)")
    
    print("\nStep 6: Check window state")
    print(f"  Visible: {window.isVisible()}")
    print(f"  Size: {window.size().width()}x{window.size().height()}")
    
    print("\nStep 7: Enter event loop")
    print("  Close window to exit")
    
    return app.exec_()

if __name__ == '__main__':
    try:
        test_step_by_step()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()