#!/bin/bash
cd api_service
pip install -r requirements.txt
python -m pytest test.py
