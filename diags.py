import threading, sys, traceback, time

def dump():
    print("=== DUMPING STACK TRACES ===")
    for id, frame in sys._current_frames().items():
        print(f"Thread {id}:")
        traceback.print_stack(frame)
    sys.exit(1)

threading.Timer(2, dump).start()
print("Importing run...")
import run
print("Import completed!")
sys.exit(0)
