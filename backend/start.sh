#!/bin/bash
cd /home/opc/Hope/backend
source venv/bin/activate
exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
