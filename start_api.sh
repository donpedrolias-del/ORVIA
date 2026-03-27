#!/bin/bash
cd generated_projects/$(ls -t generated_projects | head -1)
python3 backend.py &
echo "API démarrée sur http://127.0.0.1:5002"
