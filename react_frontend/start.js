const { execSync } = require('child_process');

const isRailway = process.env.RAILWAY_ENVIRONMENT_NAME;

if (isRailway) {
  console.log('🚀 Starting in Railway cloud...');
  execSync('npx serve -s dist', { stdio: 'inherit' });
} else {
  console.log('🧪 Starting in local dev mode...');
  execSync('react-scripts start', { stdio: 'inherit' });
}
