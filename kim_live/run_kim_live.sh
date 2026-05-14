#!/bin/zsh
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
cd /Users/dryehoshuapython/.kim_live || exit 1
exec /Library/Developer/CommandLineTools/usr/bin/python3 -u /Users/dryehoshuapython/.kim_live/server.py
