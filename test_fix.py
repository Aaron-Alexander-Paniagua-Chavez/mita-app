#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test that the configuration changes work correctly
from config.settings import MYSQL_DATABASE
from ui.app import MitaApp
import tkinter

# Mock tkinter to prevent GUI from showing
original_mainloop = tkinter.Tk.mainloop if hasattr(tkinter.Tk, 'mainloop') else None
def mock_mainloop(self):
    pass
if original_mainloop:
    tkinter.Tk.mainloop = mock_mainloop

print("Testing configuration fix...")
print(f"MYSQL_DATABASE from settings: {MYSQL_DATABASE}")

# Test that the app can start and connect to MySQL
try:
    app = MitaApp()
    print(f"MySQL ready: {app.db_service.mysql_ready}")
    print(f"MySQL warnings: {app.db_service.startup_warnings}")

    # Test connection
    conn = app.db_service.obtener_conexion_mysql()
    if conn:
        print("MySQL connection: SUCCESS")
        conn.close()
    else:
        print("MySQL connection: FAILED")

    # Test that configurator shows correct default
    # We can't easily test the GUI without displaying it, but we can verify
    # the logic in the configurator method

    app.destroy()
    print("Test completed successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()