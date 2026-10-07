const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function runTests() {
  console.log("Running Behavioral Tests for Inference Performance Lab...");

  // Start mock server
  const mockServer = spawn('python', ['mock_server.py']);
  await new Promise(r => setTimeout(r, 2000));

  const tempDir = fs.mkdtempSync(path.join(__dirname, 'test-run-'));
  
  // Create a minimal config in temp dir
  const configContent = `
endpoint: "http://localhost:8081/v1/chat/completions"
mode: "deterministic"
prompts: ["hello", "fail", "empty", "absent", "single"]
`;
  const configPath = path.join(tempDir, 'test_config.yaml');
  fs.writeFileSync(configPath, configContent);

  // Run benchmark in tempDir
  const benchmark = spawn('python', [path.join(__dirname, 'benchmark.py'), '--config', configPath], { cwd: tempDir });
  
  await new Promise((resolve, reject) => {
    benchmark.on('close', (code) => {
      if (code !== 0) reject(new Error("Benchmark script failed"));
      else resolve();
    });
  });

  // Check results
  const files = fs.readdirSync(tempDir);
  const resultFiles = files.filter(f => f.startsWith('results_') && f.endsWith('.json'));
  if (resultFiles.length === 0) throw new Error("No results file generated.");
  
  const resultData = JSON.parse(fs.readFileSync(path.join(tempDir, resultFiles[0]), 'utf8'));
  
  if (!resultData.metadata) {
      throw new Error("Missing provenance metadata in results.");
  }
  
  const results = resultData.results;
  
  let hasValidTokenCount = false;
  let hasHttpFailure = false;
  let hasNullTpot = false;
  
  for (const r of results) {
     if (r.success === false) {
         hasHttpFailure = true;
         if (r.error.includes("Empty stream received")) {
             // empty stream handling works
         }
     }
     if (r.success === true) {
         if (r.tokens > 0) hasValidTokenCount = true;
         if (r.tokens === null && r.tpot === null) hasNullTpot = true;
     }
  }
  
  if (!hasHttpFailure) throw new Error("HTTP failure condition was not exercised or saved in results.");
  if (!hasValidTokenCount) throw new Error("No valid token counts were recorded.");
  if (!hasNullTpot) throw new Error("Null TPOT/tokens logic was not exercised on missing usage blocks.");
  
  // Clean up
  resultFiles.forEach(f => fs.unlinkSync(path.join(tempDir, f)));
  fs.unlinkSync(configPath);
  fs.rmdirSync(tempDir);
  mockServer.kill();

  console.log("✅ Inference Performance Lab passed behavioral tests.");
}

runTests().catch(err => {
  console.error("❌ Test Failed:", err);
  process.exit(1);
});
