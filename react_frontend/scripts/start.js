const { execSync } = require('child_process');

const isRailway = process.env.RAILWAY_ENVIRONMENT_NAME;
const port = process.env.PORT || 3000; // Railway sets this automatically

if (isRailway) {
  console.log(`🚀 Starting in Railway cloud on port ${port}...`);
  execSync(`npx serve -s dist -l tcp://0.0.0.0:${port}`, { stdio: 'inherit' });
} else {
  console.log('🧪 Starting in local dev mode...');
  execSync('react-scripts start', { stdio: 'inherit' });
}
