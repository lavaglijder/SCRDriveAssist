FPS = 30
VERSION = "0ss.1-DEV"
DEBUG = True

# features
# points/xp change overview (1 << 0)
# automatic speed control (Two modes: [Speedlimit, Signals and speedlimits]) (mode 1: 1 << 1, mode 2: 1 << 9)
# automatic AWS Ackknowledge (async) (1 << 2)
# automatic guard bell (1 << 3)
# automatic doors (1 << 4)
# automatic termination (1 << 5)
# automatic stopping (1 << 6)
# automatic continuing route (1 << 7)
# automatic horn (async) (1 << 8)
# automatic slowdown (speedlimit) in compatible with 1 << 9 or 1 << 1 (1 << 10)

features_enabled = 0
# features_enabled = 0 + (1 << 6) + (1 << 2) + (1 << 4)
