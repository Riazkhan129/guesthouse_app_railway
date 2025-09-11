const express = require("express");
const path = require("path");
const { exec } = require("child_process");

const app = express();

// Serve the React app from dist/
app.use(express.static(path.join(__dirname, "dist")));

app.listen(3000, () => {
  console.log("✅ App running on http://localhost:3000");
});

// Open Chrome after server starts
setTimeout(() => {
  exec('start chrome "http://localhost:3000"');
}, 1500);
