// Load environment variables from .env.local
const fs = require('fs');
const path = require('path');

// Read .env.local file if it exists
const envLocalPath = path.join(__dirname, '.env.local');
const envVars = {
  NODE_ENV: 'production',
  PORT: 3000,
};

if (fs.existsSync(envLocalPath)) {
  const envContent = fs.readFileSync(envLocalPath, 'utf8');
  envContent.split('\n').forEach(line => {
    // Skip empty lines and comments
    if (!line || line.trim().startsWith('#')) return;

    const [key, ...valueParts] = line.split('=');
    if (key && valueParts.length > 0) {
      envVars[key.trim()] = valueParts.join('=').trim();
    }
  });
  console.log('.env.local 파일을 성공적으로 로드했습니다.');
} else {
  console.warn('.env.local 파일을 찾을 수 없습니다. 기본 설정을 사용합니다.');
  // Fallback to hardcoded values if .env.local doesn't exist
  envVars.NEXT_PUBLIC_API_URL = 'https://7w5nco7xn4.execute-api.us-east-1.amazonaws.com/dev';
  envVars.REVALIDATE_SECRET = 'd5aed293ec4993ad6b13a4033b3b73986b40206cd6d6f43018b3ec0f01bc2748';
}

module.exports = {
  apps: [
    {
      name: 'sedaily-eng',
      script: 'server.js',
      env: envVars,
    },
  ],
};
