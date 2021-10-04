#!/bin/bash
watch -n 0.5 -c 'date +%s | toilet -f mono9 | egrep -v "^\s+$"'
