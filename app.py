from flask import Flask, jsonify, request, send_from_directory,render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import os
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, 
            static_folder='public', 
            template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)  

# In app.py
CORS(app, origins=[
    "https://csi-battleroyale.vercel.app",
    "http://localhost:5000"  # For local dev
])

CORS(app, resources={r"/*": {"origins": [
    "https://csi-battleroyale.vercel.app",  # Production
    "http://localhost:5000"
]}})

# Database connection verification function
# In app.py, update database initialization
def verify_db_connection():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            print(f"🗄️ Database version: {result.scalar()}")
        return True
    except Exception as e:
        print(f"❌ Database verification failed: {str(e)}")
        return False
    
# Hardcoded passwords (modify these as needed)
USER_PASSWORDS = {
    "Dragonheart": "dragonify123",
    "Shadowmage": "shadowfight456",
    "Ironclad": "ironchin789",
    "Frostweaver": "frostbites012",
    "Stormbringer": "stormynights345",
    "Nightshade": "nightshaders678",
    "Emberblade": "emberfire901",
    "Thunderfist": "thunderbolt234",
    "Earthshaker": "earthyboy567",
    "Voidwalker": "voidcrazy890",
    "mp": "mp"
}

ROOM_PASSWORDS = {
    "Forgotten Crypt": "cryptrootspass",
    "Dragon's Lair": "lairdenpass",
    "Obsidian Tower": "twintowerpass",
    "Enchanted Forest": "forestfirepass",
    "Celestial Observatory": "starynightpass",
    "Ancient Ruins": "ruinswaterypass",
    "Shadow Realm": "shadowfightingpass",
    "Crystal Cavern": "crystalizedpass",
    "Thunder Peak": "thunderypass",
    "Frostfire Summit": "frostypass",
    "mp": "mp"
}

QUESTIONS = [
    {
        "id": 1,
        "title": "Question 1",
        "text": "In a frantic time-traveling battle royale, you’ve landed in the Chief Timekeeper’s office, where historic moments are tracked not by names, but by secret location IDs. You and a rival split up, each scouring for clues, and compile two lists of these IDs. But when you compare them, they’re a mess! Your list: [3, 4, 2, 1, 3, 3]; your rival’s: [4, 3, 5, 3, 9, 3]. To gain an edge, sort both lists, pair the numbers (smallest to smallest, and so on), and calculate the total distance by summing the differences between each pair. In this case, it’s 1-3 (2), 2-3 (1), 3-3 (0), 3-4 (1), 3-5 (2), 4-9 (5), totaling 11. With your own lists in hand, what’s the total distance between them to outmaneuver your foe?",
        "answer": "1151792",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 2,
        "title": "Question 2",
        "text": "The battle intensifies as you dodge temporal rifts in the Chief Timekeeper’s office. Now, you need to outsmart your rival by syncing your timelines. Using the same lists from your last clash—yours: [3, 4, 2, 1, 3, 3]; theirs: [4, 3, 5, 3, 9, 3]—calculate a similarity score to measure your edge. For each number in your list, multiply it by how many times it appears in your rival’s list, then sum the results. Here, it’s 3 * 3 (9) + 4 * 1 (4) + 2 * 0 (0) + 1 * 0 (0) + 3 * 3 (9) + 3 * 3 (9) = 31. With your own lists of location IDs, what’s your similarity score to dominate this time-warped duel?",
        "answer": "21790168",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 3,
        "title": "Question 3",
        "text": "As the battle royale rages on, you’ve hacked into the Timekeeper’s reactor logs, revealing reports of timeline levels—each a list of numbers like [7, 6, 4, 2, 1]. Your rival’s destabilizing the Red-Nosed reactor, and only “safe” reports can save it. A report is safe if its levels all increase or all decrease, with adjacent levels differing by 1 to 3. From the logs—[7, 6, 4, 2, 1], [1, 2, 7, 8, 9], [9, 7, 6, 2, 1], [1, 3, 2, 4, 5], [8, 6, 4, 4, 1], [1, 3, 6, 7, 9]—only [7, 6, 4, 2, 1] (all decreasing) and [1, 3, 6, 7, 9] (all increasing) are safe, totaling 2. With your own unusual data of reports, how many are safe to keep the reactor—and your lead—intact?",
        "answer": "334",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 4,
        "title": "Question 4",
        "text": "The reactor’s overheating in this time-warped showdown, but you’ve activated the Problem Dampener—a device that lets the Red-Nosed reactor ignore one bad level in a report. A report is still safe if its levels all increase or decrease (differing by 1 to 3), but now, removing one level from an unsafe report can make it safe. From the logs—[7, 6, 4, 2, 1], [1, 2, 7, 8, 9], [9, 7, 6, 2, 1], [1, 3, 2, 4, 5], [8, 6, 4, 4, 1], [1, 3, 6, 7, 9]—it’s now 4 safe: [7, 6, 4, 2, 1] (already safe), [1, 3, 2, 4, 5] (remove 3), [8, 6, 4, 4, 1] (remove third 4), and [1, 3, 6, 7, 9] (already safe). With your own data and the Dampener active, how many reports are now safe to secure your victory?",
        "answer": "400",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 5,
        "title": "Question 5",
        "text": "Amid the chaos, you’ve hijacked the Timekeeper’s computer to gain an edge, but its memory is a corrupted mess—your puzzle input. The program’s meant to multiply numbers with instructions like mul(X,Y), where X and Y are 1-3 digit numbers (e.g., mul(44,46) = 2024). Junk like mul(4*), mul[3,7!, or ?(12,34) is invalid and ignored. In a sample—xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))—only mul(2,4), mul(5,5), mul(11,8), and mul(8,5) work, summing to 163 (8 + 25 + 88 + 40). Scan your corrupted memory for valid mul instructions and add their results—what’s the total to outwit your rival in this temporal brawl?",
        "answer": "187833789",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 6,
        "title": "Question 6",
        "text": "Your rival’s tampered with the Timekeeper’s computer, adding twists to the corrupted memory. Alongside mul(X,Y) instructions, now do() enables future multiplications, while don’t() disables them—only the latest one counts, starting with mul enabled. In a sample—xmul(2,4)&mul[3,7]!^don’t()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))—don’t() disables mul(5,5) and mul(11,8), but do() re-enables mul(8,5). Only mul(2,4) and mul(8,5) run, summing to 48 (8 + 40). With your own corrupted memory, handle do() and don’t()—what’s the total of just the enabled multiplications to turn the tide in this time-bending fight?",
        "answer": "94455185",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 7,
        "title": "Question 7",
        "text": "A sneaky Elf, hiding in the Timekeeper’s station, interrupts your hunt for the Chief with a cryptic word search—your puzzle input. She needs you to find every instance of “XMAS” to unlock a temporal vault before your rival does. The word can appear horizontal, vertical, diagonal, backward, or overlapping.Scour your own word search grid—how many times does XMAS appear to claim the vault’s secrets and stay ahead in this time-twisted brawl?",
        "answer": "2530",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 8,
        "title": "Question 8",
        "text": "The Elf smirks as you fumble, revealing the word search’s true challenge—it’s not XMAS, it’s X-MAS! You need to find two “MAS” (forward or backward) crossing in an X shape, like M.S / .A. / M.S, with an A at the center. Your rival’s closing in on the vault, so scour your word search again—how many X-MAS patterns can you find to unlock the prize and keep your lead in this temporal slugfest?",
        "answer": "1921",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 9,
        "title": "Question 9",
        "text": "The scholars head to sub-basement 17, but an Elf at the North Pole printing station flags you down amid the Christmas rush. The sleigh launch safety manuals won’t print right, and your rival’s sabotage could doom the launch. Each update’s pages (e.g., 75,47,61,53,29) must follow rules like X|Y (X before Y), listed as 47|53, 97|13, etc. With your own rules and updates, find the correctly-ordered ones—what’s the sum of their middle page numbers to thwart your foe and save the launch?",
        "answer": "4957",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 10,
        "title": "Question 10",
        "text": "While the Elves print the safe updates, you seize the chance to outmaneuver your rival by fixing the botched ones. Using the same rules (e.g., 47|53, 97|75), reorder the incorrectly-ordered updates from before: 75,97,47,61,53 becomes 97,75,47,61,53; 61,13,29 becomes 61,29,13; 97,13,75,29,47 becomes 97,75,47,29,13. Their new middle pages—47, 29, 47—sum to 123. With your own list of updates, find the ones out of order, reorder them per the rules, and calculate—what’s the sum of their middle page numbers to flip the script in this time-twisted clash?",
        "answer": "6938",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 11,
        "title": "Question 11",
        "text": "The Historians lead you to a rickety rope bridge in a jungle, the Chief likely on the far side. Engineers are calibrating it after young elephants stole the operators (+ and *) from their equations—your puzzle input. Each line (e.g., 190: 10 19) has a test value and numbers; insert operators (evaluated left-to-right, no rearranging) to match it.Your rival’s racing to cross first—find which of your equations can be true with + and *; what’s the sum of their test values to fix the bridge and claim the lead?",
        "answer": "538191549061",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 12,
        "title": "Question 12",
        "text": "The engineers panic—your last calibration total’s off, and you spot the trick: sly elephants hid a third operator, concatenation (||), merging digits left-to-right (e.g., 12 || 345 = 12345). With + and * already in play, revisit the equations. From before, 190: 10 * 19, 3267: 81 + 40 * 27, and 292: 11 + 6 * 16 + 20 still work, but now 156: 15 || 6, 7290: 6 * 8 || 6 * 15, and 192: 17 || 8 + 14 also fit, summing all six test values to 11,387. Your rival’s mocking your delay—recheck your equations with || added; what’s the new total calibration result to stabilize the bridge and surge ahead?",
        "answer": "34612812972206",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 13,
        "title": "Question 13",
        "text": "A submarine warp drops you among amphipods, and while The Historians crash into walls hunting the Chief, a frantic amphipod begs for help with his disk—your puzzle input, like 2333133121414131402. It’s a map alternating file and free-space lengths (e.g., 12345 = file 1, free 2, file 3, free 4, file 5). Files have IDs from 0 left-to-right (0..111....22222). Compact it by moving blocks from the end to the leftmost free space until no gaps remain (e.g., 12345 becomes 022111222......). For 2333133121414131402, it ends as 0099811188827773336446555566; then, compute a checksum: multiply each block’s position (0-based) by its file ID, summing them (e.g., 1928). Compact your disk and outpace your rival—what’s the filesystem checksum?",
        "answer": "6242766523059",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 14,
        "title": "Question 14",
        "text": "The disk’s compacted, but the amphipod’s computer lags—your block-by-block fix fragmented it too much. He’s got a new plan: move whole files to the leftmost free space big enough, starting with the highest file ID (e.g., 8 in 00...111...2...333.44.5555.6666.777.888899), one move per file. If no space fits leftward, it stays put. From that sample, it shifts to 00992111777.44.333....5555.6666.....8888.., with a checksum (position * ID summed) of 2858. Your rival’s mocking the slowdown—redo your disk compaction with this whole-file method; what’s the new filesystem checksum to speed things up and strike back?",
        "answer": "6272188244509",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    },
    {
        "id": 15,
        "title": "Question 15",
        "text": "You land at a Lava Production Facility on a floating island. A hard-hatted reindeer boops your leg and hands you a scorched “Lava Island Hiking Guide” and a blank topographic map—your puzzle input (e.g., 0123 / 1234 / 8765 / 9876). A hiking trail starts at a tile with height 0, ends at 9, and moves only up/down/left/right, increasing by exactly 1 each step. A trailhead (tile with height 0) scores by counting how many 9s it can reach via such trails. Your rival’s already scouting ahead—fill in your map’s trails and compute the sum of all trailhead scores to guide the reindeer and gain the edge.",
        "answer": "798",
        "compiler": "https://github.com/ash01825/csi-algo-anar/tree/main"
    }
    # Add more questions as needed
]

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=False)
    health = db.Column(db.Integer, default=2)
    vest_purchased = db.Column(db.Boolean, default=False)
    roomid = db.Column(db.String(20), nullable=False)
   
    __table_args__ = (
        db.UniqueConstraint('username', 'roomid', name='unique_player_room'),
    )


# filepath: d:\Desktop\trial1\app.py
#@app.route('/')
#def game():
#    return render_template('index.html')

@app.before_request
def check_auth():
    if request.path == '/login' and request.method == 'POST':
        return  # Skip auth check for login endpoint
    if request.path.startswith('/static'):
        return  # Skip auth check for static files

@app.route('/login', methods=['POST'])
def login():
    try:
        print("\n🔑 Login attempt received")
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400
            
        # Convert to lowercase for case-insensitive matching
        username = data.get('username', '').strip().lower()
        roomid = data.get('roomid', '').strip().lower()
        username_pw = data.get('usernamePassword', '')
        room_pw = data.get('roomPassword', '')

        # Validate inputs
        if not all([username, roomid, username_pw, room_pw]):
            return jsonify({"error": "Missing required fields"}), 400

        # Case-sensitive password check
        if USER_PASSWORDS.get(username.title()) != username_pw:  # Match title case
            return jsonify({"error": "Invalid warrior password"}), 401
            
        if ROOM_PASSWORDS.get(roomid.title()) != room_pw:  # Match title case
            return jsonify({"error": "Invalid arena passphrase"}), 401

        db_username = username.title()
        db_roomid = roomid.title()
        # Database operations
        with db.session.no_autoflush:  # Prevent premature flushes
            player = Player.query.filter_by(
                username=username.title(),  # Store in title case
                roomid=roomid.title()       # Store in title case
            ).first()

            if not player:
                new_player = Player(
                    username=db_username,
                    roomid=db_roomid,
                    health=2
                )
                db.session.add(new_player)
                db.session.commit()  # Explicit commit for new entries
                return jsonify({
                    "message": "New player created",
                    "health": 2,
                }), 201
            else:
                # Explicit refresh for existing players
                db.session.refresh(player)
                return jsonify({
                    "message": "Welcome back",
                    "health": player.health
                }), 200

    except IntegrityError as e:
        app.logger.error(f"Integrity Error: {str(e)}")
        db.session.rollback()
        return jsonify({
            "error": "Player already exists in this arena",
            "details": "This warrior already battles in this realm"
        }), 409
    except Exception as e:
        app.logger.error(f"Critical Error: {str(e)}", exc_info=True)
        db.session.rollback()
        print(f"🔥 Critical Error: {str(e)}")
        return jsonify({
            "error": "Arcane forces disrupt the portal",
            "details": str(e)
        }), 500

@app.route('/current-health/<username>/<roomid>')
def get_current_health(username, roomid):
    player = Player.query.filter_by(username=username, roomid=roomid).first()
    if not player:
        return jsonify({"error": "Player not found"}), 404
        
    return jsonify({
        "health": player.health
    }), 200

@app.route('/questions/<roomid>')
def get_questions(roomid):
    return jsonify(QUESTIONS), 200

@app.route('/validate-answer', methods=['POST'])
def validate_answer():
    data = request.json
    question = next((q for q in QUESTIONS if q['id'] == data['questionId']), None)
    
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    is_correct = data['answer'].strip() == question['answer']
    return jsonify({"correct": is_correct}), 200

@app.route('/attack', methods=['POST'])
def attack():
    data = request.json
    target = data['target']
    roomid = data['roomid']
    
    target_player = Player.query.filter_by(username=target, roomid=roomid).first()
    if not target_player:
        return jsonify({"error": "Player not found"}), 404
    
    # Update health but don't go below 0
    target_player.health = max(0, target_player.health - 1)
    db.session.commit()
    
    return jsonify({
        "message": f"Successfully attacked {target}",
        "newHealth": target_player.health,
        "isAlive": target_player.health > 0  # New field
    }), 200

# Modified buy-vest endpoint
@app.route('/buy-vest', methods=['POST'])
def buy_vest():
    data = request.json
    username = data['username']
    roomid = data['roomid']
    
    player = Player.query.filter_by(username=username, roomid=roomid).first()
    if not player:
        return jsonify({"error": "Player not found"}), 404
    
    if player.vest_purchased:
        return jsonify({"error": "Already purchased a vest"}), 400
    
    player.health += 1
    player.vest_purchased = True
    db.session.commit()
    
    return jsonify({
        "message": "Vest purchased successfully",
        "newHealth": player.health
    }), 200

# app.py
@app.route('/players/<roomid>')
def get_players(roomid):
    players = Player.query.filter_by(roomid=roomid).all()
    return jsonify([{
        "username": p.username,
        "health": p.health,
        "vest_purchased": p.vest_purchased
    } for p in players]), 200

# app.py
@app.route('/players/<username>/<roomid>')
def get_player_state(username, roomid):
    player = Player.query.filter_by(username=username, roomid=roomid).first()
    if not player:
        return jsonify({"error": "Player not found"}), 404
        
    return jsonify({
        "health": player.health,
        "vest_purchased": player.vest_purchased,
    }), 200

if __name__ == '__main__':
    with app.app_context():
        # Verify database connection before creating tables
        if verify_db_connection():
            db.create_all()
            print("🗃️  Database tables created/verified")
        else:
            print("❌ Aborting application startup due to database connection issues")
            exit(1)
    
    # Only start the server if database connection succeeded
    app.run(host='0.0.0.0', port=5000, debug=True)
