"""
BJJ Mat IQ - Phase 1 Review Tool Configuration
Complete BJJ taxonomy: positions, actions, submissions, assessments, drills, rulesets
"""

POSITIONS = {
    "Standing": [
        "Neutral Standing", "Collar Tie", "Underhook", "Double Underhooks",
        "Russian Tie", "Two-on-One", "Body Lock Standing", "Front Headlock Standing",
        "Snap Down Position"
    ],
    "Clinch": [
        "Over-Under Clinch", "Double Collar Clinch", "Body Lock Clinch",
        "Whizzer Clinch", "Inside Tie"
    ],
    "Takedown Positions": [
        "Single Leg Setup", "Double Leg Setup", "High Crotch Position",
        "Duck Under Position", "Ankle Pick Position", "Body Lock Takedown Setup",
        "Hip Throw Setup (Ogoshi)", "Foot Sweep Position", "Drop Seoi Nage Setup",
        "Uchi Mata Setup", "Sprawl Defense", "Guillotine Defense Standing",
        "Kimura Trap Standing", "Arm Drag Position"
    ],
    "Open Guard": [
        "Open Guard", "Seated Guard", "Butterfly Guard", "Shin-to-Shin",
        "Single Leg X (SLX)", "X-Guard", "De La Riva (DLR)", "Reverse De La Riva (RDLR)",
        "Spider Guard", "Lasso Guard", "Collar-Sleeve Guard", "Worm Guard"
    ],
    "Closed Guard": [
        "Closed Guard", "High Guard", "Rubber Guard", "Overhook Closed Guard"
    ],
    "Half Guard": [
        "Half Guard (Top)", "Half Guard (Bottom)", "Deep Half Guard",
        "Knee Shield Half Guard", "Z-Guard", "Lockdown Half Guard",
        "Coyote Half Guard"
    ],
    "Guard (Other)": [
        "Inverted Guard", "50/50 Guard", "K-Guard", "Tornado Guard",
        "Waiter Guard", "Williams Guard"
    ],
    "Passing Positions": [
        "Headquarters (HQ)", "Over-Under Pass Position", "Double Under Pass Position",
        "Leg Drag Position", "Long Step Position", "Knee Slice Position",
        "Torreando Position", "Body Lock Pass Position", "Smash Pass Position",
        "Stack Pass Position"
    ],
    "Dominant Positions (Top)": [
        "Side Control", "Kesa Gatame (Scarf Hold)", "North-South",
        "Knee on Belly", "Mount", "High Mount", "S-Mount",
        "Technical Mount", "Gift Wrap Mount"
    ],
    "Back Control": [
        "Back Control (Hooks In)", "Back Control (Body Triangle)",
        "Back Control (One Hook)", "Truck Position",
        "Twister Side Control", "Rear Body Lock"
    ],
    "Leg Entanglements": [
        "Ashi Garami (Standard)", "Inside Sankaku (411/Honeyhole)",
        "Outside Ashi", "50/50 Leg Entanglement", "Saddle",
        "Game Over Position", "Cross Ashi"
    ],
    "Turtle": [
        "Turtle (Top/Attacking)", "Turtle (Bottom/Defending)",
        "Front Turtle (Sprawl)", "Seat Belt Turtle Control"
    ],
    "Scramble": [
        "Scramble", "Inversion", "Re-Guard Attempt",
        "Takedown Exchange", "Wrestling Up"
    ]
}

ACTIONS = {
    "Scoring / Takedowns": [
        "Takedown (Single Leg)", "Takedown (Double Leg)", "Takedown (Body Lock)",
        "Takedown (Snap Down)", "Takedown (Foot Sweep)", "Takedown (Hip Throw / Ogoshi)",
        "Takedown (Drop Seoi Nage)", "Takedown (Uchi Mata)", "Guard Pull",
        "Sweep", "Reversal", "Knee on Belly Transition"
    ],
    "Passing": [
        "Guard Pass Attempt", "Guard Pass Complete",
        "Pressure Pass", "Speed Pass", "Leg Drag Pass",
        "Knee Slice Pass", "Torreando Pass"
    ],
    "Submissions": [
        "Submission Attempt", "Submission Locked In", "Submission Finish (Tap)",
        "Submission Escaped"
    ],
    "Transitions / Positional": [
        "Mount Achieved", "Back Take", "Side Control Transition",
        "Position Advance", "Position Lost", "Guard Retention",
        "Re-Guard", "Scramble Won", "Scramble Lost"
    ],
    "Grip / Control": [
        "Grip Established", "Grip Broken", "Collar Grip Secured",
        "Sleeve Grip Secured", "Pant Grip Secured", "Underhook Won",
        "Underhook Lost", "Dominant Grip Achieved"
    ],
    "Penalties / Stalling": [
        "Advantage Earned", "Penalty Received", "Stalling Warning",
        "DQ (Illegal Technique)"
    ],
    "Defense": [
        "Escape (Mount)", "Escape (Side Control)", "Escape (Back)",
        "Frame Established", "Hip Escape (Shrimp)", "Bridge",
        "Granby Roll", "Turtle Recovery"
    ],
    "Missed Opportunities": [
        "Missed Scoring Opportunity", "Missed Position Advancement",
        "Missed Submission Finish", "Missed Defense/Escape", 
        "Missed Guard Pass", "Missed Sweep", 
        "Missed Back Take", "Missed Mount",
        "Missed Counter Attack", "Missed Grip Control",
        "Missed Takedown Prevention", "Missed Position Maintenance",
        "Missed Pressure Application", "Missed Timing",
        "Missed Combination Setup", "Missed Momentum Usage"
    ]
}

SUBMISSIONS = {
    "Gi Chokes": [
        "Cross Collar Choke", "Loop Choke", "Baseball Bat Choke",
        "Bow and Arrow Choke", "Ezekiel Choke (Gi)", "Brabo Choke (Gi)",
        "Clock Choke", "Paper Cutter Choke", "Breadcutter Choke",
        "Collar Drag to Choke"
    ],
    "No-Gi Chokes": [
        "Rear Naked Choke (RNC)", "Guillotine (Standard)", "Guillotine (High Elbow / Marcelotine)",
        "Guillotine (Arm-In)", "D'Arce Choke", "Anaconda Choke",
        "North-South Choke", "Von Flue Choke", "Triangle Choke (Front)",
        "Triangle Choke (Rear)", "Triangle Choke (Side)", "Mounted Triangle",
        "Ezekiel Choke (No-Gi)", "Head and Arm Choke", "Short Choke (Turtle)"
    ],
    "Arm Locks": [
        "Armbar (From Guard)", "Armbar (From Mount)", "Armbar (From Back)",
        "Armbar (Belly Down)", "Kimura", "Americana (Keylock)",
        "Omoplata", "Wrist Lock", "Baratoplata",
        "Tarikoplata", "Monoplata"
    ],
    "Leg Locks": [
        "Straight Ankle Lock", "Heel Hook (Inside)", "Heel Hook (Outside)",
        "Knee Bar", "Toe Hold", "Calf Slicer",
        "Estima Lock", "Aoki Lock", "Electric Chair"
    ],
    "Cranks / Other": [
        "Can Opener", "Neck Crank", "Twister",
        "Banana Split", "Crucifix"
    ]
}

TACTICAL_TAGS = {
    "Grip Game": [
        "Strong grip fighting", "Grip broke opponent's posture",
        "Lost grip battle", "Failed to establish grips",
        "Controlled collar tie", "Dominant sleeve control"
    ],
    "Positioning and Base": [
        "Excellent base", "Poor base / easily swept",
        "Strong hip positioning", "Poor hip control",
        "Over-committed weight", "Under-committed weight", 
        "Off-balanced opponent", "Maintained center of gravity", 
        "Lost inside position"
    ],
    "Timing and Pace": [
        "Great timing on attack", "Late on reaction",
        "Controlled the pace", "Rushed attack",
        "Patient setup", "Explosive transition",
        "Stalled momentum", "Capitalized on opponent's mistake"
    ],
    "Defense and Escapes": [
        "Strong defensive frames", "Weak frames / collapsed",
        "Early escape attempt", "Late escape attempt",
        "Survived bad position", "Failed escape led to submission",
        "Effective use of underhook", "Turtled instead of re-guarding"
    ],
    "Strategy and IQ": [
        "Good game plan execution", "Adjusted mid-match",
        "Predictable attacks", "Set up combinations",
        "Used feints effectively", "Fell into opponent's game",
        "Controlled distance well", "Failed to impose game",
        "Smart use of clock", "Poor clock awareness"
    ],
    "Athleticism and Attributes": [
        "Superior strength", "Superior flexibility",
        "Superior cardio", "Fading cardio late",
        "Explosive movement", "Heavy pressure",
        "Good scrambling ability", "Used size advantage well"
    ]
}

ASSESSMENT_AREAS = {
    "Takedowns / Stand-Up": "Ability to score takedowns or pull guard effectively",
    "Takedown Defense": "Ability to defend takedowns and maintain position",
    "Guard Pulling": "Effectiveness of guard pull entries and timing",
    "Guard Passing": "Ability to pass various guard types",
    "Guard Retention": "Ability to maintain and recover guard",
    "Sweeps": "Ability to sweep from bottom positions",
    "Submissions (Offense)": "Ability to set up and finish submissions",
    "Submission Defense": "Ability to defend and escape submissions",
    "Back Takes": "Ability to take and secure the back",
    "Back Escapes": "Ability to escape back control",
    "Mount Offense": "Ability to maintain mount and attack",
    "Mount Escapes": "Ability to escape mount positions",
    "Side Control Offense": "Ability to maintain side control and attack",
    "Side Control Escapes": "Ability to escape side control",
    "Leg Lock Offense": "Ability to enter and finish leg locks",
    "Leg Lock Defense": "Ability to defend leg lock entries and escapes",
    "Grip Fighting": "Ability to win the grip battle",
    "Transitions": "Fluidity of movement between positions",
    "Pressure / Top Game": "Ability to apply and maintain pressure from top",
    "Pace / Cardio": "Ability to maintain pace throughout the match",
    "Composure / IQ": "Decision-making and calmness under pressure",
    "Overall Game Plan": "Effectiveness of strategy and adjustments"
}

RATING_LABELS = {
    1: "Significant Weakness",
    2: "Needs Work",
    3: "Competent",
    4: "Strong",
    5: "Elite"
}

DRILL_RECOMMENDATIONS = {
    "Takedowns / Stand-Up": [
        "Single leg chain drill (setup > shot > finish > reset)",
        "Snap down to front headlock series",
        "Collar tie to inside trip reps",
        "Foot sweep timing drill (partner walking)"
    ],
    "Takedown Defense": [
        "Sprawl reaction drill (partner shoots randomly)",
        "Whizzer to re-guard flow",
        "Underhook pummeling (3 min rounds)",
        "Frame and circle drill"
    ],
    "Guard Pulling": [
        "Collar-sleeve pull to immediate sweep attempt",
        "Guard pull to shin-to-shin entry",
        "Guard pull to closed guard posture break"
    ],
    "Guard Passing": [
        "Torreando to knee slice chain drill",
        "Over-under pass pressure reps",
        "Leg drag to side control drill",
        "Headquarters position reset drill",
        "Body lock pass to mount flow"
    ],
    "Guard Retention": [
        "Hip escape (shrimp) to guard recovery reps",
        "Knee shield re-framing drill",
        "Granby roll to open guard drill",
        "Frame > hip escape > re-guard flow (5 min rounds)"
    ],
    "Sweeps": [
        "Scissor sweep setup drill",
        "Butterfly sweep to immediate top pressure",
        "De La Riva sweep to leg drag",
        "Pendulum sweep timing drill",
        "Flower sweep from closed guard reps"
    ],
    "Submissions (Offense)": [
        "Armbar from guard setup chain",
        "Triangle entry from multiple positions",
        "Kimura grip to sweep or submit flow",
        "Submission chain: armbar > triangle > omoplata"
    ],
    "Submission Defense": [
        "Hitchhiker armbar escape drill",
        "RNC defense hand fighting reps",
        "Triangle defense posture drill",
        "Stack pass from triangle/armbar attempts"
    ],
    "Back Takes": [
        "Seat belt to hooks entry drill",
        "Chair sit back take from turtle",
        "Back take from side control gift wrap",
        "Arm drag to back take flow"
    ],
    "Back Escapes": [
        "Back escape to guard recovery drill",
        "Hand fighting to strip hooks reps",
        "Escape to turtle to re-guard flow",
        "Boot scoot to clear body triangle"
    ],
    "Mount Offense": [
        "Mount maintenance drill (partner bucks/shrimps)",
        "High mount progression to armbar/choke",
        "Gift wrap from mount to back take",
        "S-mount to armbar entry drill"
    ],
    "Mount Escapes": [
        "Trap and roll (upa) escape reps",
        "Elbow-knee escape drill",
        "Heel drag escape variation drill",
        "Mount escape to half guard flow"
    ],
    "Side Control Offense": [
        "Kimura > armbar > north-south choke chain",
        "Knee on belly transition drill",
        "Side control to mount progression",
        "Paper cutter choke setup reps"
    ],
    "Side Control Escapes": [
        "Frame > hip escape > re-guard drill",
        "Underhook escape to single leg",
        "Ghost escape (going to knees) drill",
        "Guard recovery from bottom side control flow"
    ],
    "Leg Lock Offense": [
        "Ashi garami entry from SLX drill",
        "Inside heel hook finishing mechanics reps",
        "Straight ankle lock setup and finish",
        "50/50 heel hook entry drill",
        "Saddle entry from various positions"
    ],
    "Leg Lock Defense": [
        "Boot and scoot escape drill",
        "Leg lock defense: hide the heel reps",
        "50/50 escape to top position",
        "Rolling out of ashi garami drill"
    ],
    "Grip Fighting": [
        "2-on-1 grip break to own grip establishment",
        "Collar and sleeve grip fighting rounds",
        "Strip and regrip speed drill",
        "Grip endurance training (gi pull-ups, towel hangs)"
    ],
    "Transitions": [
        "Positional sparring: advance one position at a time",
        "Flow rolling with transition focus (no subs)",
        "Chain wrestling: takedown to pass to mount flow",
        "Scramble recovery to dominant position drill"
    ],
    "Pressure / Top Game": [
        "Shoulder pressure maintenance drill",
        "Cross-face and hip pressure reps",
        "Heavy top ride: partner tries to escape (3 min)",
        "Knee on belly pressure and transition drill"
    ],
    "Pace / Cardio": [
        "Match simulation rounds (full match length at comp pace)",
        "Shark tank: fresh partner every 2 minutes",
        "Sprint drilling: 30 sec max reps of technique",
        "Positional sparring with shorter rest intervals"
    ],
    "Composure / IQ": [
        "Bad position sparring: start in mount bottom, back control bottom",
        "Decision-making drill: coach calls position changes",
        "Competition simulation with referee and points",
        "Film study: watch and narrate your own matches"
    ],
    "Overall Game Plan": [
        "Game plan rehearsal: drill your A-game sequence",
        "Positional sparring from your weakest position",
        "Strategy sessions: map your ideal path to submission/points",
        "Competition simulation with specific game plan constraints"
    ]
}

RULESETS = {
    "IBJJF": {
        "name": "IBJJF (International Brazilian Jiu-Jitsu Federation)",
        "scoring": {
            "Takedown": 2,
            "Sweep": 2,
            "Knee on Belly": 2,
            "Guard Pass": 3,
            "Mount": 4,
            "Back Control (w/ hooks)": 4,
            "Advantage": 0.5,
            "Penalty": -1
        },
        "notes": "Advantages break ties. Heel hooks illegal for most belt levels. Reaping illegal. Match times vary by belt."
    },
    "ADCC": {
        "name": "ADCC (Abu Dhabi Combat Club)",
        "scoring": {
            "Takedown (to guard)": 2,
            "Takedown (clean, past guard)": 4,
            "Sweep": 2,
            "Knee on Belly (3 sec)": 2,
            "Guard Pass": 3,
            "Mount": 2,
            "Back Mount (w/ hooks)": 3,
            "Penalty": -1
        },
        "notes": "No points in first half of regulation. Negative points for guard pulling in second half. All leg locks legal."
    },
    "Sub-Only": {
        "name": "Submission Only",
        "scoring": {},
        "notes": "No points. Match won by submission only. Overtime rules vary by organization (EBI overtime, etc.)."
    },
    "NAGA": {
        "name": "NAGA (North American Grappling Association)",
        "scoring": {
            "Takedown": 2,
            "Sweep": 2,
            "Knee on Belly": 2,
            "Guard Pass": 3,
            "Mount": 4,
            "Back Control (w/ hooks)": 4,
            "Advantage": 0.5,
            "Penalty": -1
        },
        "notes": "Similar to IBJJF. Some divisions allow heel hooks at advanced levels."
    }
}

BELT_LEVELS = [
    # Kids Belt System (4-15 years old)
    "Kids White", "Kids White-Gray (1 stripe)", "Kids White-Gray (2 stripes)", 
    "Kids White-Gray (3 stripes)", "Kids White-Gray (4 stripes)",
    "Kids Gray", "Kids Gray-Black (1 stripe)", "Kids Gray-Black (2 stripes)", 
    "Kids Gray-Black (3 stripes)", "Kids Gray-Black (4 stripes)",
    "Kids Yellow", "Kids Yellow-White (1 stripe)", "Kids Yellow-White (2 stripes)", 
    "Kids Yellow-White (3 stripes)", "Kids Yellow-White (4 stripes)",
    "Kids Orange", "Kids Orange-White (1 stripe)", "Kids Orange-White (2 stripes)", 
    "Kids Orange-White (3 stripes)", "Kids Orange-White (4 stripes)",
    "Kids Green", "Kids Green-White (1 stripe)", "Kids Green-White (2 stripes)", 
    "Kids Green-White (3 stripes)", "Kids Green-White (4 stripes)",
    
    # Adult Belt System (16+ years old)
    "White", "Blue", "Purple", "Brown", "Black", "Coral (Red-Black)", "Red Belt"
]

WEIGHT_CLASSES = [
    "Rooster", "Light Feather", "Feather", "Light",
    "Middle", "Medium Heavy", "Heavy", "Super Heavy",
    "Ultra Heavy", "Absolute / Open"
]

AGE_DIVISIONS = ["Juvenile", "Adult", "Master 1", "Master 2", "Master 3", "Master 4", "Master 5+"]

GI_NOGI = ["Gi", "No-Gi"]

MOMENT_RESULTS = [
    "No Points", "Takedown", "Sweep", "Knee on Belly", 
    "Guard Pass", "Mount", "Back Control (w/ hooks)", 
    "Takedown (to guard)", "Takedown (clean, past guard)", 
    "Back Mount (w/ hooks)", "Knee on Belly (3 sec)",
    "Advantage", "Penalty", 
    "Takedown Attempt (Advantage)", "Sweep Attempt (Advantage)", 
    "Guard Pass Attempt (Advantage)", "Submission Attempt (Advantage)",
    "Submission Finish"
]

MISSED_OPPORTUNITIES = [
    "None", "Could have scored points", "Could have improved position",
    "Could have finished submission", "Could have defended better",
    "Could have passed guard", "Could have swept", 
    "Could have taken back", "Could have mounted",
    "Could have escaped", "Could have controlled grips",
    "Could have prevented takedown", "Could have countered attack",
    "Could have maintained position", "Could have applied more pressure",
    "Could have been more explosive", "Could have timed attack better",
    "Could have set up combination", "Could have used opponent's momentum"
]

BJJ_REASONS = {
    "Offensive Strategy": [
        "Set up submission attack", "Create scoring opportunity", 
        "Advance position for points", "Break opponent's posture",
        "Establish dominant grips", "Build attacking momentum", 
        "Execute game plan", "Capitalize on opponent's mistake",
        "Create submission chain", "Force opponent to react"
    ],
    "Defensive Response": [
        "Escape bad position", "Prevent submission attempt",
        "Deny opponent's grips", "Counter opponent's attack",
        "Neutralize opponent's pressure", "Defend points being scored",
        "Recover guard", "Stop position advance",
        "Break opponent's rhythm", "Survive and reset"
    ],
    "Positional Control": [
        "Maintain current advantage", "Control distance",
        "Apply pressure on opponent", "Pin opponent down",
        "Secure better angle", "Establish frames",
        "Clear opponent's frames", "Create space to move",
        "Control opponent's hips", "Improve body position"
    ],
    "Tactical Adjustment": [
        "Change game plan mid-match", "Adjust to opponent's style",
        "Exploit discovered weakness", "Counter opponent's strategy",
        "Test new technique", "Mix up attacks",
        "Force opponent out of comfort zone", "Create unpredictability",
        "Respond to referee instructions", "Manage match time"
    ],
    "Physical/Mental": [
        "Tire out opponent", "Apply consistent pressure",
        "Test opponent's cardio", "Break opponent's confidence",
        "Demonstrate dominance", "Slow down fast opponent",
        "Speed up slow opponent", "Impose physical style",
        "Conserve energy", "Reset mental state"
    ]
}