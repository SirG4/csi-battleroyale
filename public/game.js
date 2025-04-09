let currentUser = null;
let currentRoom = null;
let questions = [];
let selectedQuestion = null;
let updateInterval;
let availableQuestions = [];
let lastKnownHealth = 2; 
const API_BASE_URL = 'https://csi-battleroyale.onrender.com';

// Update the login function in game.js
async function login() {
    // Get input values
    currentUser = document.getElementById('username').value;
    currentRoom = document.getElementById('roomId').value;
    const usernamePassword = document.getElementById('usernamePassword').value;
    const roomPassword = document.getElementById('roomPassword').value;

    // Validate inputs
    if (!currentUser || !currentRoom || !usernamePassword || !roomPassword) {
        alert('All fields must be filled!');
        return;
    }

    try {
        // 1. Authentication
        const authResponse = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                username: currentUser,
                roomid: currentRoom,
                usernamePassword: usernamePassword,
                roomPassword: roomPassword
            })
        });

        // Handle non-JSON responses first
        const authText = await authResponse.text();
        let authData;
        try {
            authData = JSON.parse(authText);
        } catch {
            throw new Error(`Invalid server response: ${authText.slice(0, 50)}`);
        }

        if (!authResponse.ok) {
            throw new Error(authData.error || 'Authentication failed');
        }

        // 2. Load game data
        const [questionsRes, playerRes] = await Promise.all([
            fetch(`${API_BASE_URL}/questions/${currentRoom}`),
            fetch(`${API_BASE_URL}/players/${currentUser}/${currentRoom}`)
        ]);

        // Handle responses safely
        const [questionsText, playerText] = await Promise.all([
            questionsRes.text(),
            playerRes.text()
        ]);

        let questionsData, playerData;
        try {
            questionsData = JSON.parse(questionsText);
            playerData = JSON.parse(playerText);
        } catch {
            throw new Error('Invalid game data received');
        }

        if (!questionsRes.ok) throw new Error('Failed to load questions');
        if (!playerRes.ok) throw new Error('Failed to load player data');

        // Initialize game state
        window.questions = questionsData;
        lastKnownHealth = playerData.health;
        updateHealthDisplay(lastKnownHealth);
        startHealthMonitor();
        availableQuestions = window.questions.map(q => q.id);
        showQuestionList();

    } catch (error) {
        alert(`Failed to enter arena: ${error.message}`);
    }
}

function startHealthMonitor() {
    const healthCheck = setInterval(async () => {
        const response = await fetch(`${API_BASE_URL}/players/${currentUser}/${currentRoom}`);
        if (response.ok) {
            const data = await response.json();
            
            if (data.health <= 0) {
                clearInterval(healthCheck);
                showGameOver();
                return;
            }
            
            if (data.health < lastKnownHealth) {
                showAttackNotification();
                updateHealthDisplay(data.health);
            }
            
            lastKnownHealth = data.health;
        }
    }, 3000);
}

function updateHealthDisplay(newHealth) {
    document.getElementById('healthValue').textContent = newHealth;
    document.getElementById('healthValue').classList.add('health-alert');
    setTimeout(() => {
        document.getElementById('healthValue').classList.remove('health-alert');
    }, 1000);
}

function showAttackNotification() {
    const notification = document.createElement('div');
    notification.className = 'attack-notification';
    notification.innerHTML = `
        <div class="attack-alert">
            <h3>⚔️ You've Been Attacked! ⚔️</h3>
            <p>Your life force has diminished!</p>
        </div>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function showQuestionList() {
    // Hide all sections
    document.getElementById('login').style.display = 'none';
    document.getElementById('questionView').style.display = 'none';
    document.getElementById('actions').style.display = 'none';
    document.getElementById('playersList').style.display = 'none';
    document.getElementById('gameOver').style.display = 'none';
    
    // Show only question selection
    document.getElementById('questionSelection').style.display = 'block';
    
    // Filter questions based on available IDs
    const filteredQuestions = window.questions.filter(q => 
        availableQuestions.includes(q.id)
    );
    
    const container = document.getElementById('questionsList');
    container.innerHTML = filteredQuestions.map(q => `
        <div class="question-item" onclick="showQuestion(${q.id})">
            <h3>${q.title}</h3>
        </div>
    `).join('');
    
    document.getElementById('questionSelection').style.display = 'block';
}

async function showQuestion(questionId) {
    // Return to list if no question selected
    if (!questionId) {
        showQuestionList();
        return;
    }

    // Find and display the question
    selectedQuestion = window.questions.find(q => q.id === questionId);

    if (!selectedQuestion) {
        alert('Question not found!');
        showQuestionList();
        return;
    }
    
    document.getElementById('questionSelection').style.display = 'none';
    document.getElementById('questionView').style.display = 'block';
    
    // Populate question details
    document.getElementById('questionTitle').textContent = selectedQuestion.title;
    document.getElementById('questionText').textContent = selectedQuestion.text;
    document.getElementById('compilerLink').href = selectedQuestion.compiler;
    document.getElementById('answer').value = '';
}

async function submitAnswer() {
    const answer = document.getElementById('answer').value.trim();
    
    const response = await fetch(`${API_BASE_URL}/validate-answer`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: currentUser,
            roomid: currentRoom,
            questionId: selectedQuestion.id,
            answer: answer
        })
    });
    
    const result = await response.json();
    if (result.correct) {
        // Remove from available questions
        availableQuestions = availableQuestions.filter(id => id !== selectedQuestion.id);
        await loadPlayers(); 
        showActions();
        alert('Correct answer! Challenge conquered!');
    } else {
        alert('Incorrect! The mystical forces reject your answer!');
    }
}

async function showAttackList() {
    const response = await fetch(`${API_BASE_URL}/players/${currentRoom}`);
    const players = await response.json();
    
    const container = document.getElementById('players');
    container.innerHTML = players
        .filter(p => p.username !== currentUser)
        .map(p => `
            <div class="player-card" onclick="attack('${p.username}')">
                <h3>${p.username}</h3>
                <p>Health: ${p.health} ❤️</p>
            </div>
        `).join('');
    
    document.getElementById('actions').style.display = 'none';
    document.getElementById('playersList').style.display = 'block';
}

function showActions() {
    // Hide all sections
    document.getElementById('login').style.display = 'none';
    document.getElementById('questionSelection').style.display = 'none';
    document.getElementById('questionView').style.display = 'none';
    document.getElementById('playersList').style.display = 'none';
    document.getElementById('gameOver').style.display = 'none';
    
    // Show only actions
    document.getElementById('actions').style.display = 'block';
}

async function attack(target) {
    try {
    const response = await fetch(`${API_BASE_URL}/attack`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            username: currentUser, 
            roomid: currentRoom,
            target 
        })
    });
    
    const data = await response.json();
    if (response.ok) {
        await loadPlayers();
        const newHealth = data.newHealth > 0 ? data.newHealth : '💀 DEAD 💀';
        alert(`⚔️ Successful strike! ${target}'s health: ${newHealth}`);
        document.getElementById('questionSelection').scrollIntoView({ behavior: 'smooth' });
        showQuestionList();
    }
    else{
        alert('Failed to Attack')
    }
    } catch (error) {
        alert('Failed to execute attack - check your connection!');
    }
}

async function buyVest() {
    try {
        const response = await fetch(`${API_BASE_URL}/buy-vest`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                username: currentUser, 
                roomid: currentRoom 
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            lastKnownHealth = data.newHealth;
            updateHealthDisplay(data.newHealth);

            await loadPlayers();

            alert(`🛡️ Armor reinforced! New life force: ${data.newHealth}`);
            
            showQuestionList();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Failed to buy vest');
    }
}

async function updateGameState() {
    const response = await fetch(`${API_BASE_URL}/player/${currentUser}/${currentRoom}`);
    const state = await response.json();
    
    // Update health display with animation
    const healthElement = document.querySelector(`.player-${currentUser} .health`);
    if (healthElement) {
        healthElement.classList.add('health-update');
        setTimeout(() => healthElement.classList.remove('health-update'), 500);
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 3000);
}

// Update loadPlayers to handle health display
async function loadPlayers() {
    const response = await fetch(`${API_BASE_URL}/players/${currentRoom}`);
    const players = await response.json();
    const container = document.getElementById('players');
    container.innerHTML = players
        .map(p => `
            <div class="player">
                <span>${p.username}</span>
                <span>${p.health} ❤️</span>
                ${p.vest_purchased ? '🛡️' : ''}
            </div>
        `).join('');
    
    // Check if current player is dead
    const currentPlayer = players.find(p => p.username === currentUser);
    if (currentPlayer && currentPlayer.health === 0) {
        showGameOver();
    }
}

function showGameOver() {
    // Hide all elements
    document.querySelectorAll('.mystical-box, #questionSelection').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show game over screen
    const gameOverDiv = document.getElementById('gameOver');
    gameOverDiv.style.display = 'block';
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'game-over-overlay';
    document.body.appendChild(overlay);
    
    // Disable all buttons
    document.querySelectorAll('button').forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.style.cursor = 'not-allowed';
    });
    
    // Stop all intervals
    clearInterval(updateInterval);
    
    // Prevent navigation
    window.onbeforeunload = null;
    window.location.hash = 'no-back';
    window.history.pushState(null, null, window.location.href);
    
    // Block keyboard input
    document.onkeydown = function(e) {
        e.preventDefault();
        return false;
    };
}