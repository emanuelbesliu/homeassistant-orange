#!/bin/bash
# Test Orange.ro API
# 
# Usage: 
#   ./run_test.sh
#
# You will be prompted for credentials

echo "🔐 Orange.ro API Test"
echo ""
echo "Enter your Orange.ro credentials:"
read -p "Email/Username: " ORANGE_USER
read -sp "Password: " ORANGE_PASS
echo ""
echo ""

export ORANGE_USER
export ORANGE_PASS

python3 test_orange_api_simple.py
