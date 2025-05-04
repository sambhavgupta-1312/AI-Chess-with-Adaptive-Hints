# ai_call.py
import json
import requests
import time
import random

# Set to True to use mock responses instead of real AI service
USE_MOCK = False

def get_mock_response(difficulty, board_state):
    """Generate mock AI responses for testing without the AI service"""
    # Simple mock responses based on difficulty
    mock_responses = {
        "Beginner": [
            "Consider developing your knights and bishops toward the center of the board.",
            "Watch out for pieces that are under attack but not defended.",
            "Try to control the center squares - they're important for mobility.",
            "Make sure your king is safe - consider castling if you haven't already."
        ],
        "Intermediate": [
            "Look for tactical opportunities like pins or forks with your knights.",
            "Your pawn structure could be strengthened by advancing your central pawns.",
            "Consider the long-term position of your pieces rather than immediate captures.",
            "Your opponent has some weaknesses on the kingside that could be exploited."
        ],
        "Hardcore": [
            "The e-file is semi-open. Who will control it?",
            "Pawn tension in the center - resolve it only when advantageous.",
            "Knight outpost potential on d5.",
            "Your light-squared bishop lacks scope. Consider restructuring."
        ]
    }
    
    # Default to Beginner if difficulty not found
    difficulty_key = "Beginner"
    for key in mock_responses:
        if key.lower() in difficulty.lower():
            difficulty_key = key
            break
    
    # Choose a random response from the appropriate difficulty level
    return random.choice(mock_responses[difficulty_key])

def ai_call(state: str, prompt: str, model: str = "llama2", max_retries: int = 2) -> str:
    """Call AI with retry mechanism and better error handling
    
    Args:
        state: The game state representation
        prompt: The prompt to send to the AI
        model: AI model to use (default: llama2)
        max_retries: Maximum number of retries on failure
        
    Returns:
        AI response or fallback message
    """
    # If mock mode is enabled, return mock responses instead of calling the API
    if USE_MOCK:
        return get_mock_response(prompt, state)
        
    full_prompt = f"{prompt.strip()}\n\nState:\n{state.strip()}\n\nAI:"
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': full_prompt,
                    'stream': False
                },
                timeout=10  # Add timeout to prevent hanging
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', 'No response from AI.').strip()
        
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                time.sleep(1)  # Wait a bit before retrying
                continue
            return "Error: The AI service took too long to respond. Please try again."
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries:
                time.sleep(1)
                continue
            return "Error: Could not connect to the AI service. Is it running?"
            
        except requests.exceptions.RequestException as e:
            print(f"AI call failed (attempt {attempt+1}/{max_retries+1}): {e}")
            if attempt < max_retries:
                time.sleep(1)
                continue
            
            # Provide fallback hint when all retries fail
            fallbacks = {
                "Beginner": "Consider developing your pieces toward the center of the board and watching for threats to your pieces.",
                "Intermediate": "Look for pieces that aren't defended and consider how you might improve your position.",
                "Hardcore": "Sometimes the best move isn't the most obvious one. Think about long-term positional advantages."
            }
            
            # Try to extract difficulty from prompt
            difficulty = "Beginner"  # Default
            if "intermediate" in prompt.lower():
                difficulty = "Intermediate"
            elif "hardcore" in prompt.lower() or "advanced" in prompt.lower():
                difficulty = "Hardcore"
                
            return f"Error: Failed to get response from AI. Here's a general tip: {fallbacks[difficulty]}"

