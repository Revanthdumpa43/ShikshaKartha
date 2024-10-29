// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAQLoRpzO4u2XwEwNtZqJpj6OJO9M8pLAU",
    authDomain: "shikshakartha.firebaseapp.com",
    projectId: "shikshakartha",
    storageBucket: "shikshakartha.appspot.com",
    messagingSenderId: "97296245",
    appId: "1:97296245:web:34a36303eb87a2d7c97d3c"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();

// Handle Signup
const signupForm = document.getElementById('signup-form');
if (signupForm) {
    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;

        console.log('Attempting to sign up with:', email);

        auth.createUserWithEmailAndPassword(email, password)
            .then(userCredential => {
                console.log('User signed up:', userCredential.user);
                return db.collection('users').doc(userCredential.user.uid).set({
                    email: email,
                    createdAt: firebase.firestore.FieldValue.serverTimestamp()
                });
            })
            .then(() => {
                console.log('Redirecting to dashboard after signup');
                window.location.href = '/'; // Redirect to dashboard
            })
            .catch(error => {
                console.error('Signup error:', error);
                document.getElementById('signup-error').textContent = error.message;
            });
    });
}

// Handle Login
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        auth.signInWithEmailAndPassword(email, password)
            .then(userCredential => {
                console.log('Logged in:', userCredential.user);
                window.location.href = '/index.html'; // Redirect to index.html after login
            })
            .catch(error => {
                document.getElementById('login-error').textContent = error.message;
            });
    });
}

