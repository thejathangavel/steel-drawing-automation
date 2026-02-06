try:
    import pymongo
    print(f"PyMongo version: {pymongo.__version__}")
    try:
        from pymongo import cursor_shared
        print("pymongo.cursor_shared exists")
    except ImportError:
        print("pymongo.cursor_shared does NOT exist")
except ImportError:
    print("PyMongo not installed")
