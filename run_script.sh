#!/bin/bash
#!/usr/bin/env python

sleep 10
python src/fixtures.py
uvicorn src.main:app --host 0.0.0.0 --port 8002
