#!/bin/sh

forever -l updog.log stop updog; git pull --rebase; forever -a -l updog.log --uid "updogbot" -a -c python run.py;