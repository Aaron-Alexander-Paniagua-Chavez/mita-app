#!/usr/bin/env python3
"""Punto de entrada MITA."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import main

if __name__ == "__main__":
    main()
