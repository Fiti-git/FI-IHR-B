#!/usr/bin/env python
"""
Test script for the Job Offer API endpoint
This script demonstrates how to use the new POST /api/job-offer/create endpoint
"""

import json

# Example request payload as specified in the requirements
test_request_payload = {
    "application_id": 789,
    "offer_details": {
        "salary": 70000,
        "start_date": "2025-11-01",
        "benefits": ["Health Insurance", "Paid Leave"]
    },
    "offer_status": "Pending"  # Options: "Pending", "Accepted", "Rejected"
}

# Example expected response
expected_response = {
    "offer_id": 456,
    "message": "Job offer created successfully",
    "application_id": 789,
    "offer_details": {
        "salary": 70000,
        "start_date": "2025-11-01",
        "benefits": ["Health Insurance", "Paid Leave"]
    },
    "offer_status": "Pending"
}

print("=== JOB OFFER CREATE API TEST ===")
print()
print("Endpoint: POST /api/job-offer/create")
print()
print("Request Payload:")
print(json.dumps(test_request_payload, indent=2))
print()
print("Expected Response (201 Created):")
print(json.dumps(expected_response, indent=2))
print()
print("Database Storage Format:")
print("offer_details TextField will contain:")
print('{"salary": 70000, "start_date": "2025-11-01", "benefits": ["Health Insurance", "Paid Leave"]}')
print()

# Example validation errors
print("=== VALIDATION EXAMPLES ===")
print()

# Missing required fields
invalid_payload_1 = {
    "application_id": 789,
    "offer_details": {
        "salary": 70000,
        # Missing "start_date" and "benefits"
    }
}

print("Invalid Request (Missing fields):")
print(json.dumps(invalid_payload_1, indent=2))
print("Expected Response (400 Bad Request):")
print(json.dumps({
    "error": "Invalid data",
    "details": {
        "offer_details": ["Missing required fields in offer_details: start_date, benefits"]
    }
}, indent=2))
print()

# Invalid salary
invalid_payload_2 = {
    "application_id": 789,
    "offer_details": {
        "salary": "invalid_salary",
        "start_date": "2025-11-01",
        "benefits": ["Health Insurance"]
    }
}

print("Invalid Request (Invalid salary):")
print(json.dumps(invalid_payload_2, indent=2))
print("Expected Response (400 Bad Request):")
print(json.dumps({
    "error": "Invalid data",
    "details": {
        "offer_details": ["Salary must be a valid number"]
    }
}, indent=2))
print()

# Invalid date format
invalid_payload_3 = {
    "application_id": 789,
    "offer_details": {
        "salary": 70000,
        "start_date": "01-11-2025",  # Wrong format
        "benefits": ["Health Insurance"]
    }
}

print("Invalid Request (Invalid date format):")
print(json.dumps(invalid_payload_3, indent=2))
print("Expected Response (400 Bad Request):")
print(json.dumps({
    "error": "Invalid data",
    "details": {
        "offer_details": ["start_date must be in YYYY-MM-DD format"]
    }
}, indent=2))
print()

print("=== CURL COMMAND EXAMPLES ===")
print()
print("# Create a job offer")
print("curl -X POST http://localhost:8000/api/job-offer/create/ \\")
print("  -H \"Content-Type: application/json\" \\")
print("  -d '{}'".format(json.dumps(test_request_payload).replace("'", "\\'")))
print()

print("# Get job offer details")
print("curl -X GET http://localhost:8000/api/job-offer/456/")
print()

print("# Accept job offer")
print("curl -X POST http://localhost:8000/api/job-offer/accept/ \\")
print("  -H \"Content-Type: application/json\" \\")
print("  -d '{\"offer_id\": 456}'")
print()

print("# Reject job offer")
print("curl -X POST http://localhost:8000/api/job-offer/reject/ \\")
print("  -H \"Content-Type: application/json\" \\")
print("  -d '{\"offer_id\": 456}'")
print()

print("=== IMPLEMENTATION FEATURES ===")
print()
print("✅ Validates application_id exists")
print("✅ Validates application status is 'Accepted'")
print("✅ Prevents duplicate offers for same application")
print("✅ Validates offer_details structure (salary, start_date, benefits)")
print("✅ Validates salary is positive number")
print("✅ Validates start_date format (YYYY-MM-DD)")
print("✅ Validates benefits is a list")
print("✅ Stores offer_details as JSON in database")
print("✅ Returns structured response with all details")
print("✅ Includes Swagger documentation")
print("✅ Proper error handling with detailed messages")