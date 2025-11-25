try:
    import webrtcvad
    print("webrtcvad imported successfully")
except ImportError as e:
    print(f"webrtcvad import failed: {e}")

try:
    import resemblyzer
    print("resemblyzer imported successfully")
except ImportError as e:
    print(f"resemblyzer import failed: {e}")
