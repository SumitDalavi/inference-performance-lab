const assert = require('assert');
const fs = require('fs');

async function runTests() {
  console.log("Running Inference Performance Lab Tests...");
  
  const benchmarkCode = fs.readFileSync(__dirname + '/benchmark.py', 'utf8');
  
  // Test 1: HTTP failures
  assert(benchmarkCode.includes("results_log.append({\"success\": False, \"error\":"), "Gate 7 Failed: HTTP failures not appended to results.");
  
  // Test 2: Chunk counts mathematically segregated
  assert(benchmarkCode.includes("chunk_count += 1"), "Gate 7 Failed: Chunks not segregated from tokens.");
  assert(benchmarkCode.includes("usage.get('completion_tokens')"), "Gate 7 Failed: Tokens not fetched from usage telemetry.");
  
  console.log("✅ Inference Performance Lab passed.");
}

runTests().catch(err => {
  console.error(err);
  process.exit(1);
});
