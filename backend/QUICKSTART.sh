#!/usr/bin/env bash
# Quick Start Guide: APK Analysis with Risk Scoring Integration

echo "=================================="
echo "FraudShield AI - Risk Assessment Integration"
echo "=================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Validate Integration${NC}"
echo "Running validation checks..."
python validate_integration.py

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ Validation failed. Check the output above.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Validation passed!${NC}\n"

echo -e "${BLUE}Step 2: Start Backend Server${NC}"
echo "Starting FraudShield AI backend on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# The following steps are for manual testing after server is running in another terminal:
echo ""
echo -e "${BLUE}Step 3: Test Workflow (in another terminal)${NC}"
echo ""
echo "Create analysis:"
echo 'curl -X POST http://localhost:8000/api/v1/analysis \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '"'"'{
echo '    "apk_name": "test.apk",
echo '    "package_name": "com.test.app",
echo '    "file_path": "./test.apk",
echo '    "file_hash": "abc123",
echo '    "version_code": "1"
echo '  }'"'"
echo ""
echo "Run analysis (includes risk scoring):"
echo "curl -X POST http://localhost:8000/api/v1/analysis/1/run"
echo ""
echo "Verify database:"
echo "sqlite3 ./data/fraudshield.db 'SELECT id, risk_score, severity FROM analyses;'"
