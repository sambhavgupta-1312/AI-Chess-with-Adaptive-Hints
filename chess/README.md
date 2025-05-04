# Chess Game with Smart Hint System

A chess game implementation with a dynamic, AI-powered hint system designed to help players improve their game.

## Features

### Game Features
- Standard chess rules and gameplay
- Player vs. Player mode
- Visual move highlighting

### Advanced Hint System
- **Difficulty Levels**: Choose between Beginner, Intermediate, and Hardcore hint difficulty
- **Hint Types**: Select from Direct, Strategic, or Educational hint styles
- **Adaptive Feedback Loop**: The system learns from your feedback to provide better hints over time
- **Personalized Recommendations**: Suggests optimal hint settings based on your preferences
- **Skill Level Tracking**: Monitors your progress and adapts hints to your changing skill level
- **AI-Powered**: Leverages the Gemma3 AI model to provide context-aware hints

## How to Use the Hint System

1. **Get a Hint**: Click the "Suggest Move" button to receive a hint based on your current settings
2. **Adjust Difficulty**: Use the difficulty buttons on the right to change the hint complexity:
   - Beginner: Simple, direct hints suitable for new players
   - Intermediate: More nuanced hints with some strategic elements
   - Hardcore: Cryptic, advanced hints that make you think deeply

3. **Change Hint Type**: Select the type of hint you want:
   - Direct: Suggests a specific move or immediate action
   - Strategic: Focuses on positional or long-term advantages
   - Educational: Teaches chess concepts relevant to the current position

4. **Provide Feedback**: After receiving a hint, indicate whether it was helpful using the 👍 or 👎 buttons
   - This feedback helps the system adapt to your preferences and skill level
   - Gold borders highlight your preferred settings based on feedback
   - The system will occasionally suggest optimal settings for you

5. **Switch Hint Modes**: Right-click the "Suggest Move" button to toggle between:
   - AI-powered hints (default)
   - Traditional minimax algorithm suggestions (highlights the move on the board)

## Adaptive Learning

The hint system incorporates several smart features to adapt to your preferences:

- **Game Phase Detection**: Recognizes whether you're in the opening, middle game, or endgame
- **Skill Level Assessment**: Estimates your skill level based on which hints you find helpful
- **Prompt Customization**: Tailors AI prompts to include your preferences and game context
- **Preference Tracking**: Learns which hint types and difficulty levels work best for you
- **Variety Injection**: Occasionally introduces different hint styles to prevent repetitiveness

## Technical Notes

The hint system stores feedback data in `hint_feedback.json` and player profile data in `player_profile.json`. These files track:

- Hint effectiveness metrics
- Preferred hint types and difficulties
- Estimated skill level
- Game phase preferences
- Hint history

The system uses this data to continuously improve hint quality and tailor the experience to your specific needs.

## Game Menu
![menu](https://user-images.githubusercontent.com/24194821/57589722-cf907c00-74eb-11e9-9318-822abd6c9942.png)

## Gameplay
![game](https://user-images.githubusercontent.com/24194821/57589721-cf907c00-74eb-11e9-8def-bf4782315ed9.png)

## Winner Menu
![checkmate](https://user-images.githubusercontent.com/24194821/57589723-cf907c00-74eb-11e9-8b42-aef703c3e1f8.png)
