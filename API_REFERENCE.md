# 🔌 Agent Exo-Suit V5.0 API Reference

## 🎯 **API Overview**

Agent Exo-Suit V5.0 provides a comprehensive API for AI agent development, compression, pattern recognition, and system management.

---

## 🚀 **Core System API**

### **System Status & Health**

#### `get_system_status()`
Returns comprehensive system status information.

**Returns:**
```json
{
  "status": "V5_ACTIVE",
  "tools_operational": 21,
  "tools_total": 43,
  "completion_percentage": 49,
  "protection_status": "ACTIVE",
  "drift_status": "ZERO",
  "last_update": "2025-08-18"
}
```

#### `get_system_health()`
Returns detailed system health metrics.

**Returns:**
```json
{
  "health_score": 100,
  "performance_metrics": {
    "files_per_second": "207-3.7K",
    "compression_ratio": "1004.00x",
    "memory_usage": "optimized"
  },
  "protection_systems": {
    "bulletproof_protection": "ACTIVE",
    "drift_detection": "ACTIVE",
    "truth_enforcement": "ACTIVE"
  }
}
```

---

## 🧠 **Kai Integration API**

### **Consensus System**

#### `create_consensus_proposal(proposal_data)`
Creates a new consensus proposal for multi-agent validation.

**Parameters:**
- `proposal_data` (dict): Proposal details including action, reasoning, and impact

**Returns:**
```json
{
  "proposal_id": "uuid",
  "status": "PENDING",
  "sub_agent_votes": [],
  "phd_agent_votes": [],
  "kai_review": "PENDING"
}
```

#### `get_consensus_status(proposal_id)`
Retrieves the current status of a consensus proposal.

**Parameters:**
- `proposal_id` (string): Unique proposal identifier

**Returns:**
```json
{
  "proposal_id": "uuid",
  "status": "APPROVED",
  "sub_agent_consensus": "2/3",
  "phd_agent_consensus": "4/5",
  "kai_decision": "APPROVED",
  "execution_status": "PENDING"
}
```

### **Safety System**

#### `audit_agent_action(agent_id, action_data)`
Audits an agent's action for safety compliance.

**Parameters:**
- `agent_id` (string): Unique agent identifier
- `action_data` (dict): Action details and context

**Returns:**
```json
{
  "audit_id": "uuid",
  "safety_score": 95,
  "risk_assessment": "LOW",
  "recommendations": ["action_approved"],
  "compliance_status": "COMPLIANT"
}
```

---

## 🗜️ **MMH-RS Compression API**

### **Neural Entanglement Codec**

#### `compress_file(file_path, strategy='auto')`
Compresses a file using the Neural Entanglement Codec.

**Parameters:**
- `file_path` (string): Path to the file to compress
- `strategy` (string): Compression strategy ('auto', 'neural', 'pattern', 'hybrid')

**Returns:**
```json
{
  "compression_id": "uuid",
  "original_size": 1048576,
  "compressed_size": 1044,
  "compression_ratio": 1004.00,
  "strategy_used": "neural",
  "processing_time": 0.045,
  "status": "SUCCESS"
}
```

#### `decompress_file(compressed_file_path, output_path)`
Decompresses a previously compressed file.

**Parameters:**
- `compressed_file_path` (string): Path to compressed file
- `output_path` (string): Path for decompressed output

**Returns:**
```json
{
  "decompression_id": "uuid",
  "original_size": 1048576,
  "decompressed_size": 1048576,
  "integrity_check": "PASSED",
  "processing_time": 0.032,
  "status": "SUCCESS"
}
```

### **Pattern Recognition**

#### `analyze_patterns(file_path)`
Analyzes file patterns for optimal compression strategy.

**Parameters:**
- `file_path` (string): Path to the file to analyze

**Returns:**
```json
{
  "analysis_id": "uuid",
  "file_type": "text",
  "pattern_complexity": "HIGH",
  "recommended_strategy": "neural",
  "estimated_compression": 800.0,
  "confidence_score": 0.95
}
```

---

## 🛡️ **Protection System API**

### **Bulletproof Protection**

#### `protect_file(file_path, protection_level='HIGH')`
Applies bulletproof protection to a file.

**Parameters:**
- `file_path` (string): Path to the file to protect
- `protection_level` (string): Protection level ('LOW', 'MEDIUM', 'HIGH', 'MAXIMUM')

**Returns:**
```json
{
  "protection_id": "uuid",
  "file_path": "/path/to/file",
  "protection_level": "HIGH",
  "deletion_prevention": "ACTIVE",
  "drift_detection": "ACTIVE",
  "status": "PROTECTED"
}
```

#### `get_protection_status(file_path)`
Retrieves the current protection status of a file.

**Parameters:**
- `file_path` (string): Path to the protected file

**Returns:**
```json
{
  "file_path": "/path/to/file",
  "protection_status": "ACTIVE",
  "protection_level": "HIGH",
  "deletion_attempts": 0,
  "drift_events": 0,
  "last_audit": "2025-08-18T10:30:00Z"
}
```

### **Drift Detection**

#### `detect_drift(file_path)`
Detects potential drift in file content or behavior.

**Parameters:**
- `file_path` (string): Path to the file to analyze

**Returns:**
```json
{
  "drift_analysis_id": "uuid",
  "drift_detected": false,
  "drift_score": 0.02,
  "drift_type": "NONE",
  "confidence": 0.98,
  "recommendations": ["file_healthy"]
}
```

---

## 🔍 **Performance Monitoring API**

### **Real-time Metrics**

#### `get_performance_metrics()`
Retrieves real-time performance metrics.

**Returns:**
```json
{
  "timestamp": "2025-08-18T10:30:00Z",
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "gpu_usage": 23.1,
  "files_processed": 15420,
  "compression_operations": 892,
  "average_response_time": 0.045
}
```

#### `get_gpu_metrics()`
Retrieves GPU-specific performance metrics.

**Returns:**
```json
{
  "gpu_name": "RTX 4070",
  "gpu_utilization": 23.1,
  "memory_used": "4.2 GB",
  "memory_total": "12.0 GB",
  "temperature": 65,
  "power_draw": "180W",
  "performance_state": "P0"
}
```

### **Performance Optimization**

#### `optimize_performance(optimization_target='AUTO')`
Applies performance optimizations to the system.

**Parameters:**
- `optimization_target` (string): Target for optimization ('AUTO', 'CPU', 'GPU', 'MEMORY', 'COMPRESSION')

**Returns:**
```json
{
  "optimization_id": "uuid",
  "target": "AUTO",
  "optimizations_applied": [
    "memory_pooling",
    "gpu_memory_optimization",
    "compression_strategy_tuning"
  ],
  "performance_improvement": 15.3,
  "status": "COMPLETED"
}
```

---

## 🔧 **System Management API**

### **Configuration Management**

#### `get_system_config()`
Retrieves current system configuration.

**Returns:**
```json
{
  "security": {
    "localhost_only": true,
    "external_access": false,
    "security_headers": true
  },
  "performance": {
    "gpu_acceleration": true,
    "memory_optimization": true,
    "compression_strategy": "adaptive"
  },
  "protection": {
    "bulletproof_protection": true,
    "drift_detection": true,
    "truth_enforcement": true
  }
}
```

#### `update_system_config(config_updates)`
Updates system configuration.

**Parameters:**
- `config_updates` (dict): Configuration updates to apply

**Returns:**
```json
{
  "update_id": "uuid",
  "changes_applied": ["security_headers", "compression_strategy"],
  "validation_status": "PASSED",
  "restart_required": false,
  "status": "SUCCESS"
}
```

### **Maintenance Operations**

#### `run_system_maintenance(maintenance_type='FULL')`
Runs system maintenance operations.

**Parameters:**
- `maintenance_type` (string): Type of maintenance ('QUICK', 'STANDARD', 'FULL', 'DEEP')

**Returns:**
```json
{
  "maintenance_id": "uuid",
  "maintenance_type": "FULL",
  "operations_completed": [
    "cache_cleanup",
    "memory_optimization",
    "performance_tuning",
    "security_audit"
  ],
  "duration": "00:05:32",
  "status": "COMPLETED"
}
```

---

## 📊 **Analytics & Reporting API**

### **System Analytics**

#### `get_system_analytics(time_range='24H')`
Retrieves system analytics for the specified time range.

**Parameters:**
- `time_range` (string): Time range for analytics ('1H', '24H', '7D', '30D', 'ALL')

**Returns:**
```json
{
  "time_range": "24H",
  "total_files_processed": 125000,
  "average_compression_ratio": 850.5,
  "peak_performance": "3.7K files/sec",
  "system_uptime": "99.98%",
  "error_rate": "0.02%",
  "performance_trend": "IMPROVING"
}
```

#### `generate_performance_report(report_type='COMPREHENSIVE')`
Generates a comprehensive performance report.

**Parameters:**
- `report_type` (string): Type of report ('SUMMARY', 'DETAILED', 'COMPREHENSIVE')

**Returns:**
```json
{
  "report_id": "uuid",
  "report_type": "COMPREHENSIVE",
  "generation_time": "00:00:15",
  "report_size": "2.4 MB",
  "download_url": "/reports/uuid.pdf",
  "status": "READY"
}
```

---

## 🚨 **Error Handling & Status Codes**

### **HTTP Status Codes**
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### **Error Response Format**
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid file path provided",
    "details": "File path must be absolute and accessible",
    "timestamp": "2025-08-18T10:30:00Z",
    "request_id": "uuid"
  }
}
```

---

## 📚 **API Usage Examples**

### **Python Example**
```python
import requests

# Get system status
response = requests.get('http://localhost:8000/api/system/status')
status = response.json()
print(f"System completion: {status['completion_percentage']}%")

# Compress a file
compression_data = {
    'file_path': '/path/to/file.txt',
    'strategy': 'neural'
}
response = requests.post('http://localhost:8000/api/compression/compress', 
                        json=compression_data)
result = response.json()
print(f"Compression ratio: {result['compression_ratio']}x")
```

### **JavaScript Example**
```javascript
// Get system health
fetch('/api/system/health')
  .then(response => response.json())
  .then(health => {
    console.log(`Health score: ${health.health_score}`);
  });

// Create consensus proposal
const proposal = {
  action: 'update_config',
  reasoning: 'Performance optimization',
  impact: 'LOW'
};

fetch('/api/consensus/proposal', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(proposal)
})
.then(response => response.json())
.then(result => {
  console.log(`Proposal ID: ${result.proposal_id}`);
});
```

---

## 🔒 **Authentication & Security**

### **API Keys**
All API requests require a valid API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

### **Rate Limiting**
- **Standard**: 1000 requests per hour
- **Premium**: 10000 requests per hour
- **Enterprise**: 100000 requests per hour

### **Security Headers**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

---

## 📋 **API Versioning**

### **Current Version: v1.0**
- **Base URL**: `/api/v1/`
- **Status**: Stable
- **Deprecation**: None planned

### **Version Compatibility**
- **v1.0**: Current stable version
- **v0.9**: Deprecated (use v1.0)
- **v0.8**: Deprecated (use v1.0)

---

## 🎯 **Next Steps**

1. **API Testing**: Use the provided examples to test API endpoints
2. **Integration**: Integrate API calls into your applications
3. **Documentation**: Refer to this reference for all API details
4. **Support**: Contact support for additional assistance

---

**API Reference Created**: August 20, 2025  
**Version**: v1.0  
**Status**: Phase 2 Implementation 🚀  
**Target**: 100% World Release Ready 🏆
