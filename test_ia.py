#!/usr/bin/env python3
# Test script for IA service

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing IA service...")
print("=" * 50)

# Import and test IA service
try:
    from services.ia_service import AsistenteIA
    ia = AsistenteIA()

    print(f"IA service loaded successfully")
    print(f"Connected: {ia.conectado}")
    print(f"Status: {ia.estado}")

    if ia.conectado:
        print("\nTesting IA response...")
        response = ia.enviar_mensaje("Hola, ¿cómo estás?")
        print(f"Response: {response}")
    else:
        print("\nIA not connected - checking environment...")
        print(f"GEMINI_API_KEY in env: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
        if os.getenv('GEMINI_API_KEY'):
            key = os.getenv('GEMINI_API_KEY')
            print(f"Key starts with: {key[:20]}...")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test completed")