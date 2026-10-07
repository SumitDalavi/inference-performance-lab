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
  const benchmark = spawn('python', [path.join(__dirname, 'benchmark.py'), '--config', configPath], { cwd: tempDir, stdio: 'inherit' });
  
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
  
  if (results.length !== 5) throw new Error("Expected 5 results");
  
  const helloResult = results[0];
  const failResult = results[1];
  const emptyResult = results[2];
  const absentResult = results[3];
  const singleResult = results[4];

  if (helloResult.tokens !== 11) throw new Error("hello request did not record exactly 11 tokens");
  if (failResult.success !== false) throw new Error("fail request did not fail");
  if (emptyResult.success !== false || !emptyResult.error.includes("Empty stream received")) throw new Error("empty request did not fail with empty stream error");
  if (absentResult.tokens !== null || absentResult.tpot !== null) throw new Error("absent request did not record null tokens and TPOT");
  if (singleResult.tokens !== 1 || singleResult.tpot !== null) throw new Error("single request did not record 1 token and null TPOT");
  
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
