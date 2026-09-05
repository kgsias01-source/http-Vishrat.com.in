const express = require("express");
const admin = require("firebase-admin");

const app = express();

app.use(express.json());

const PORT = process.env.PORT || 10000;

// Firebase Admin
if (!admin.apps.length) {
  const serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT);

  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

const db = admin.firestore();

// Test route
app.get("/", (req, res) => {
  res.json({
    status: "ok",
    message: "Vishrat Secure Backend is running"
  });
});

// Firebase login token verify
async function verifyUser(req, res, next) {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res.status(401).json({
        error: "Login required"
      });
    }

    const idToken = authHeader.split("Bearer ")[1];

    const decodedToken = await admin.auth().verifyIdToken(idToken);

    req.user = decodedToken;

    next();
  } catch (error) {
    return res.status(401).json({
      error: "Invalid or expired login"
    });
  }
}

// Check batch access
app.get("/api/access/:batch", verifyUser, async (req, res) => {
  try {
    const batch = req.params.batch;
    const uid = req.user.uid;

    const userDoc = await db.collection("users").doc(uid).get();

    if (!userDoc.exists) {
      return res.json({
        allowed: false
      });
    }

    const data = userDoc.data();

    // LOYAL FREE ACCESS
    if (
      req.user.email === "kgsias01@gmail.com" &&
      data.freeAccess === true
    ) {
      return res.json({
        allowed: true,
        free: true,
        batch: batch
      });
    }

    // Purchased batch access
    if (
      data.batches &&
      data.batches[batch] === true
    ) {
      return res.json({
        allowed: true,
        free: false,
        batch: batch
      });
    }

    return res.json({
      allowed: false,
      batch: batch
    });

  } catch (error) {
    console.error(error);

    return res.status(500).json({
      error: "Server error"
    });
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Vishrat backend running on port ${PORT}`);
});
