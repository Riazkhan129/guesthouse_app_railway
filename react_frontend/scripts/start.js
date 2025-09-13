const { execSync } = require('child_process');

const isRailway = process.env.RAILWAY_ENVIRONMENT_NAME;
const port = process.env.PORT; 

if (!port) {
  console.error('❌ PORT environment variable is not set. Defaulting to 8080 will break Railway.');
  process.exit(1);
}

if (isRailway) {
  console.log(`🚀 Starting in Railway cloud on port ${port}...`);
  execSync(`npx serve -s dist -l ${port}`, { stdio: 'inherit' });
} else {
  console.log('🧪 Starting in local dev mode...');
  execSync('react-scripts start', { stdio: 'inherit' });
}
