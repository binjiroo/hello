import sys
from cefpython3 import cefpython as cef

def main():
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    cef.Initialize()
    browser = cef.CreateBrowserSync(url="https://www.google.com",
                                    window_title="CEF Browser")
    cef.MessageLoop()
    cef.Shutdown()

if __name__ == '__main__':
    main()
