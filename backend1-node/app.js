const express = require("express");
const app = express();

app.use(express.json());

app.get("/", (req, res) => {
  res.json({
    service: "Node.js Backend",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
    host: process.env.HOSTNAME || "node-backend",
  });
});

app.get("/users", (req, res) => {
  res.json({
    users: [
      { id: 1, name: "Alice", email: "alice@example.com" },
      { id: 2, name: "Bob", email: "bob@example.com" },
    ],
  });
});

app.post("/users", (req, res) => {
  res.status(201).json({
    message: "User created",
    user: req.body,
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Node.js backend running on port ${PORT}`);
});
