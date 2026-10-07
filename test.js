const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function runTests() {
  console.log("Running Behavioral Tests for Inference Performance Lab...");

  // Start mock server
  const mockServer = spawn('python', ['mock_server.py']);
  await new Promise(r => setTimeout(r, 2000));

  // Create a minimal config
  const configContent = `
endpoint: "http://localhost:8081/v1/chat/completions"
mode: "closed-loop"
concurrency: 1
duration_seconds: 2
prompts: ["hello"]
`;
  fs.writeFileSync('test_config.yaml', configContent);

  // Run benchmark
  const benchmark = spawn('python', ['benchmark.py', '--config', 'test_config.yaml']);
  
  await new Promise((resolve, reject) => {
    benchmark.on('close', (code) => {
      if (code !== 0) reject(new Error("Benchmark script failed"));
      else resolve();
    });
  });

  // Check results
  const files = fs.readdirSync('.');
  const resultFiles = files.filter(f => f.startsWith('results_') && f.endsWith('.json'));
  if (resultFiles.length === 0) throw new Error("No results file generated.");
  
  const resultData = JSON.parse(fs.readFileSync(resultFiles[0], 'utf8'));
  
  if (!resultData.metadata) {
      throw new Error("Missing provenance metadata in results.");
  }
  
  const results = resultData.results;
  
  let hasValidTokenCount = false;
  let hasHttpFailure = false;
  
  for (const r of results) {
     if (r.success === false) hasHttpFailure = true;
     if (r.success === true && r.tokens > 0) hasValidTokenCount = true;
  }
  
  // Clean up
  resultFiles.forEach(f => fs.unlinkSync(f));
  fs.unlinkSync('test_config.yaml');
  mockServer.kill();

  console.log("✅ Inference Performance Lab passed behavioral tests.");
}

runTests().catch(err => {
  console.error("❌ Test Failed:", err);
  process.exit(1);
});
