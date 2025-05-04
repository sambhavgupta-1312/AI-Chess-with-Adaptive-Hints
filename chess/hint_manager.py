import json
import os
import pygame
import random
from ai.aiCall import ai_call

class HintManager:
    def __init__(self):
        # Hint difficulty levels
        self.difficulty_levels = ["Beginner", "Intermediate", "Hardcore"]
        self.current_difficulty = "Beginner"
        
        # Hint types
        self.hint_types = ["Direct", "Strategic", "Educational"]
        self.current_hint_type = "Direct"
        
        # Feedback tracking
        self.feedback_data = self._load_feedback_data()
        
        # Hint UI elements
        self.difficulty_buttons = []
        self.type_buttons = []
        self.feedback_buttons = []
        
        # Current hint
        self.current_hint = ""
        self.hint_shown = False
        
        # Adaptive learning parameters
        self.adaptation_threshold = 5  # Minimum feedback needed to start adapting
        self.learning_rate = 0.8  # How much to weight recent feedback (0.0-1.0)
        self.suggestion_counter = 0  # Track consecutive hints to suggest changes
        
        # Player profile data
        self.player_profile = self._load_player_profile()
        
    def _load_feedback_data(self):
        """Load feedback data from file or create new if doesn't exist"""
        file_path = os.path.join("games", "chess", "hint_feedback.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default empty feedback data structure
        return {
            "total_hints": 0,
            "helpful_hints": 0,
            "by_difficulty": {d: {"total": 0, "helpful": 0} for d in self.difficulty_levels},
            "by_type": {t: {"total": 0, "helpful": 0} for t in self.hint_types},
            "recent_feedback": []  # Store recent feedback for trend analysis
        }
    
    def _load_player_profile(self):
        """Load player profile data or create new if doesn't exist"""
        file_path = os.path.join("games", "chess", "player_profile.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default player profile
        return {
            "preferred_difficulty": "Beginner",
            "preferred_type": "Direct",
            "skill_level": 1.0,  # 1.0-10.0 scale
            "improvement_rate": 0.0,
            "context_weights": {
                "opening": 1.0,
                "middle_game": 1.0,
                "end_game": 1.0,
                "tactical": 1.0,
                "positional": 1.0
            },
            "hint_history": []
        }
    
    def _save_feedback_data(self):
        """Save feedback data to file"""
        file_path = os.path.join("games", "chess", "hint_feedback.json")
        with open(file_path, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
    
    def _save_player_profile(self):
        """Save player profile data to file"""
        file_path = os.path.join("games", "chess", "player_profile.json")
        with open(file_path, 'w') as f:
            json.dump(self.player_profile, f, indent=2)
    
    def get_hint_effectiveness(self):
        """Calculate and return hint effectiveness percentage"""
        if self.feedback_data["total_hints"] == 0:
            return 0
        return int((self.feedback_data["helpful_hints"] / self.feedback_data["total_hints"]) * 100)
    
    def determine_game_phase(self, board_state):
        """Determine the phase of the game from the board state"""
        # Count pieces to estimate game phase
        piece_count = 0
        for line in board_state.strip().split('\n'):
            for piece in line.split():
                if piece and piece != '.':
                    piece_count += 1
        
        if piece_count > 28:
            return "opening"
        elif piece_count > 15:
            return "middle_game"
        else:
            return "end_game"
    
    def update_player_profile(self, was_helpful, board_state):
        """Update player profile based on feedback"""
        game_phase = self.determine_game_phase(board_state)
        
        # Update skill level based on feedback
        if was_helpful:
            # If player finds hardcore hints helpful, they're probably skilled
            if self.current_difficulty == "Hardcore":
                self.player_profile["skill_level"] = min(10.0, self.player_profile["skill_level"] + 0.2)
            # If they find beginner hints helpful, they might be newer
            elif self.current_difficulty == "Beginner":
                pass  # No change, finding basic hints helpful doesn't indicate skill level
        else:
            # If they don't find beginner hints helpful, might be too simple
            if self.current_difficulty == "Beginner":
                self.player_profile["skill_level"] = min(10.0, self.player_profile["skill_level"] + 0.1)
            # If they don't find hardcore hints helpful, might be too advanced
            elif self.current_difficulty == "Hardcore":
                self.player_profile["skill_level"] = max(1.0, self.player_profile["skill_level"] - 0.1)
        
        # Update context weights
        weight_change = 0.1 if was_helpful else -0.05
        self.player_profile["context_weights"][game_phase] += weight_change
        
        # Update preferred settings based on overall effectiveness
        type_effectiveness = {}
        for hint_type in self.hint_types:
            type_data = self.feedback_data["by_type"][hint_type]
            if type_data["total"] > 0:
                effectiveness = type_data["helpful"] / type_data["total"]
                type_effectiveness[hint_type] = effectiveness
        
        # If we have enough data, update preferred type
        if type_effectiveness and max(type_effectiveness.values()) > 0.6:
            self.player_profile["preferred_type"] = max(type_effectiveness, key=type_effectiveness.get)
        
        # Similarly for difficulty
        difficulty_effectiveness = {}
        for difficulty in self.difficulty_levels:
            diff_data = self.feedback_data["by_difficulty"][difficulty]
            if diff_data["total"] > 0:
                effectiveness = diff_data["helpful"] / diff_data["total"]
                difficulty_effectiveness[difficulty] = effectiveness
        
        # If we have enough data, update preferred difficulty
        if difficulty_effectiveness and max(difficulty_effectiveness.values()) > 0.6:
            self.player_profile["preferred_difficulty"] = max(difficulty_effectiveness, key=difficulty_effectiveness.get)
        
        # Add to hint history
        self.player_profile["hint_history"].append({
            "difficulty": self.current_difficulty,
            "type": self.current_hint_type,
            "helpful": was_helpful,
            "game_phase": game_phase
        })
        
        # Keep history manageable (last 100 hints)
        if len(self.player_profile["hint_history"]) > 100:
            self.player_profile["hint_history"] = self.player_profile["hint_history"][-100:]
        
        # Save changes
        self._save_player_profile()
    
    def suggest_optimal_settings(self):
        """Suggest optimal hint settings based on player profile and feedback"""
        message = None
        
        # Only make suggestions after at least 5 hints
        if self.feedback_data["total_hints"] < 5:
            return None
        
        # Increment suggestion counter
        self.suggestion_counter += 1
        
        # Only suggest changes every few hints to avoid being annoying
        if self.suggestion_counter < 3:
            return None
        
        # Reset counter
        self.suggestion_counter = 0
        
        # Check if current settings match optimal
        if (self.current_difficulty != self.player_profile["preferred_difficulty"] or 
            self.current_hint_type != self.player_profile["preferred_type"]):
            
            message = f"Based on your feedback, you might prefer {self.player_profile['preferred_difficulty']} "\
                     f"{self.player_profile['preferred_type']} hints."
        
        # Check if player might be ready to increase difficulty
        elif (self.current_difficulty == "Beginner" and 
              self.player_profile["skill_level"] > 3.0 and 
              self.suggestion_counter == 0):
            message = "You seem to be understanding the basics well. Try Intermediate difficulty for more nuanced hints!"
        
        # If player is finding hardcore hints helpful consistently
        elif (self.current_difficulty == "Hardcore" and 
              self.feedback_data["by_difficulty"]["Hardcore"]["total"] > 5 and
              self.feedback_data["by_difficulty"]["Hardcore"]["helpful"] / 
              self.feedback_data["by_difficulty"]["Hardcore"]["total"] > 0.8):
            message = "You're mastering advanced hints! You're well on your way to chess excellence."
        
        return message
    
    def process_feedback(self, was_helpful, board_state=None):
        """Process feedback for the current hint"""
        if not self.hint_shown:
            return
            
        self.feedback_data["total_hints"] += 1
        self.feedback_data["by_difficulty"][self.current_difficulty]["total"] += 1
        self.feedback_data["by_type"][self.current_hint_type]["total"] += 1
        
        if was_helpful:
            self.feedback_data["helpful_hints"] += 1
            self.feedback_data["by_difficulty"][self.current_difficulty]["helpful"] += 1
            self.feedback_data["by_type"][self.current_hint_type]["helpful"] += 1
        
        # Add to recent feedback list (limited to last 20)
        self.feedback_data["recent_feedback"].append({
            "difficulty": self.current_difficulty,
            "type": self.current_hint_type,
            "helpful": was_helpful,
            "timestamp": pygame.time.get_ticks()
        })
        
        # Keep only last 20 feedback items
        if len(self.feedback_data["recent_feedback"]) > 20:
            self.feedback_data["recent_feedback"] = self.feedback_data["recent_feedback"][-20:]
        
        # Update player profile if we have a board state
        if board_state:
            self.update_player_profile(was_helpful, board_state)
        
        self._save_feedback_data()
        self.reset_hint_state()
    
    def reset_hint_state(self):
        """Reset the hint state after feedback or when starting a new game"""
        self.hint_shown = False
        self.current_hint = ""
    
    def set_difficulty(self, difficulty):
        """Set hint difficulty level"""
        if difficulty in self.difficulty_levels:
            self.current_difficulty = difficulty
    
    def set_hint_type(self, hint_type):
        """Set hint type"""
        if hint_type in self.hint_types:
            self.current_hint_type = hint_type
    
    def generate_hint(self, board_state):
        """Generate hint based on current settings and feedback history"""
        # Update player profile if we have a current game state
        game_phase = self.determine_game_phase(board_state)
        
        # Create a personalized prompt based on player history and current settings
        prompt = self._create_adaptive_prompt(board_state, game_phase)
        
        # Make the AI call
        self.current_hint = ai_call(board_state, prompt)
        
        # Check if we should suggest different settings
        suggestion = self.suggest_optimal_settings()
        if suggestion:
            self.current_hint = f"{self.current_hint}\n\n[Suggestion: {suggestion}]"
        
        self.hint_shown = True
        return self.current_hint
    
    def _create_adaptive_prompt(self, board_state, game_phase):
        """Create an adaptive prompt based on player profile and current settings"""
        # Base prompts from original implementation
        base_prompts = {
            # Different prompt templates based on difficulty and type
            "Beginner": {
                "Direct": "Analyze this chess position and give a direct, simple hint about the best move. Explain in basic terms that a beginner would understand.",
                "Strategic": "Analyze this chess position and suggest a simple strategic concept that applies here. Keep it very basic for a beginner.",
                "Educational": "Explain one basic chess concept relevant to this position that would help a beginner improve their game."
            },
            "Intermediate": {
                "Direct": "Analyze this chess position and suggest a good move. Provide brief reasoning that an intermediate player would understand.",
                "Strategic": "Analyze this chess position and explain a mid-level strategic concept that applies here. Include some tactical considerations.",
                "Educational": "Explain an intermediate chess concept relevant to this position that would help a player improve their tactical thinking."
            },
            "Hardcore": {
                "Direct": "Analyze this chess position and give a cryptic hint about the best move. Don't reveal too much, just point in the right direction.",
                "Strategic": "Analyze this chess position and explain an advanced strategic concept that applies here. Include complex positional considerations.",
                "Educational": "Explain an advanced chess concept relevant to this position that would help a player develop deeper strategic understanding."
            }
        }
        
        # Get the base prompt
        prompt = base_prompts[self.current_difficulty][self.current_hint_type]
        
        # If we have enough feedback data, customize the prompt
        if self.feedback_data["total_hints"] >= self.adaptation_threshold:
            # Determine if player tends to prefer certain hint styles
            player_preferences = []
            
            # Check hint type effectiveness
            for hint_type in self.hint_types:
                type_data = self.feedback_data["by_type"][hint_type]
                if type_data["total"] > 2 and type_data["helpful"] / type_data["total"] > 0.7:
                    player_preferences.append(f"You tend to find {hint_type.lower()} explanations most helpful")
            
            # Check game phase preferences from player profile
            phase_weights = self.player_profile["context_weights"]
            strongest_phase = max(phase_weights, key=phase_weights.get)
            if phase_weights[strongest_phase] > 1.2:  # If significantly higher
                player_preferences.append(f"You seem to appreciate hints during the {strongest_phase.replace('_', ' ')}")
            
            # Add customization to prompt if we have preferences
            if player_preferences:
                context = " ".join(player_preferences)
                prompt = f"{prompt} Based on your feedback: {context}."
            
            # Add focus on current game phase
            prompt = f"{prompt} This appears to be the {game_phase.replace('_', ' ')}."
            
            # Add skill level adaptation
            skill_level = self.player_profile["skill_level"]
            if skill_level < 3.0 and self.current_difficulty != "Beginner":
                prompt = f"{prompt} Break down complex ideas into simpler terms."
            elif skill_level > 7.0 and self.current_difficulty == "Hardcore":
                prompt = f"{prompt} You can use advanced chess terminology."
            
            # Look at recent hint history to avoid repetition
            recent_hints = self.player_profile["hint_history"][-5:] if self.player_profile["hint_history"] else []
            recent_types = [hint["type"] for hint in recent_hints]
            
            # If we've been giving the same type repeatedly, try to vary
            if len(recent_types) >= 3 and len(set(recent_types)) == 1:
                other_types = [t for t in self.hint_types if t != recent_types[0]]
                if other_types and random.random() > 0.5:  # 50% chance to vary
                    varied_type = random.choice(other_types)
                    prompt = f"{prompt} Try to include some {varied_type.lower()} elements for variety."
        
        return prompt
    
    def create_ui_elements(self, start_x, start_y, button_width, button_height, spacing):
        """Create UI elements for hint controls"""
        # Difficulty buttons
        self.difficulty_buttons = []
        for i, difficulty in enumerate(self.difficulty_levels):
            rect = pygame.Rect(start_x, start_y + i * (button_height + spacing), button_width, button_height)
            self.difficulty_buttons.append({"rect": rect, "text": difficulty})
        
        # Hint type buttons - add more spacing between sections
        start_y += len(self.difficulty_levels) * (button_height + spacing) + spacing * 3
        self.type_buttons = []
        for i, hint_type in enumerate(self.hint_types):
            rect = pygame.Rect(start_x, start_y + i * (button_height + spacing), button_width, button_height)
            self.type_buttons.append({"rect": rect, "text": hint_type})
        
        # Feedback buttons - add even more spacing between sections
        start_y += len(self.hint_types) * (button_height + spacing) + spacing * 4
        self.feedback_buttons = [
            {"rect": pygame.Rect(start_x, start_y, button_width // 2 - 5, button_height), "text": "👍", "value": True},
            {"rect": pygame.Rect(start_x + button_width // 2 + 5, start_y, button_width // 2 - 5, button_height), "text": "👎", "value": False}
        ]
    
    def draw_controls(self, screen, font):
        """Draw hint control elements on screen"""
        # Draw no section title to reduce overlapping

        # Draw difficulty buttons - skip the "Hint Controls" title to reduce overlapping
        diff_title = pygame.font.SysFont("Arial", 14, bold=True).render("Difficulty:", True, (255, 255, 255))
        diff_y = self.difficulty_buttons[0]["rect"].y - 20
        screen.blit(diff_title, (self.difficulty_buttons[0]["rect"].x, diff_y))
        
        for btn in self.difficulty_buttons:
            # Highlight preferred difficulty with a special border
            is_preferred = btn["text"] == self.player_profile["preferred_difficulty"]
            
            color = (100, 100, 255) if btn["text"] == self.current_difficulty else (50, 50, 100)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=5)
            
            # Draw gold border around preferred setting
            if is_preferred:
                border_rect = btn["rect"].inflate(4, 4)
                pygame.draw.rect(screen, (255, 215, 0), border_rect, 2, border_radius=7)
            
            text = font.render(btn["text"], True, (255, 255, 255))
            screen.blit(text, (btn["rect"].x + (btn["rect"].width - text.get_width()) // 2, 
                              btn["rect"].y + (btn["rect"].height - text.get_height()) // 2))
        
        # Draw hint type buttons with header - proper positioning
        type_title = pygame.font.SysFont("Arial", 14, bold=True).render("Hint Type:", True, (255, 255, 255))
        type_y = self.type_buttons[0]["rect"].y - 20
        screen.blit(type_title, (self.type_buttons[0]["rect"].x, type_y))
        
        for btn in self.type_buttons:
            # Highlight preferred type with a special border
            is_preferred = btn["text"] == self.player_profile["preferred_type"]
            
            color = (100, 255, 100) if btn["text"] == self.current_hint_type else (50, 100, 50)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=5)
            
            # Draw gold border around preferred setting
            if is_preferred:
                border_rect = btn["rect"].inflate(4, 4)
                pygame.draw.rect(screen, (255, 215, 0), border_rect, 2, border_radius=7)
            
            text = font.render(btn["text"], True, (255, 255, 255))
            screen.blit(text, (btn["rect"].x + (btn["rect"].width - text.get_width()) // 2, 
                              btn["rect"].y + (btn["rect"].height - text.get_height()) // 2))
        
        # Draw feedback buttons (only if a hint is shown)
        if self.hint_shown:
            feedback_title = pygame.font.SysFont("Arial", 14, bold=True).render("Was it helpful?", True, (255, 255, 255))
            feedback_y = self.feedback_buttons[0]["rect"].y - 20
            screen.blit(feedback_title, (self.feedback_buttons[0]["rect"].x, feedback_y))
            
            for btn in self.feedback_buttons:
                pygame.draw.rect(screen, (200, 200, 80), btn["rect"], border_radius=5)
                text = font.render(btn["text"], True, (0, 0, 0))
                screen.blit(text, (btn["rect"].x + (btn["rect"].width - text.get_width()) // 2, 
                                  btn["rect"].y + (btn["rect"].height - text.get_height()) // 2))
        
        # Draw hint effectiveness - only if we have enough data
        if self.feedback_data["total_hints"] > 0:
            effect_y = self.feedback_buttons[0]["rect"].bottom + 20
            effect_text = f"Effectiveness: {self.get_hint_effectiveness()}%"
            effect_render = pygame.font.SysFont("Arial", 14, bold=True).render(effect_text, True, (255, 255, 255))
            screen.blit(effect_render, (self.feedback_buttons[0]["rect"].x, effect_y))
            
            # Draw skill level with reduced text
            if self.feedback_data["total_hints"] >= self.adaptation_threshold:
                skill_text = f"Skill: {self.player_profile['skill_level']:.1f}/10"
                skill_render = pygame.font.SysFont("Arial", 14, bold=True).render(skill_text, True, (255, 255, 255))
                screen.blit(skill_render, (self.feedback_buttons[0]["rect"].x, effect_y + 20))
    
    def handle_click(self, pos, current_board_state=None):
        """Handle clicks on hint control elements"""
        # Check difficulty buttons
        for btn in self.difficulty_buttons:
            if btn["rect"].collidepoint(pos):
                self.set_difficulty(btn["text"])
                return True
        
        # Check hint type buttons
        for btn in self.type_buttons:
            if btn["rect"].collidepoint(pos):
                self.set_hint_type(btn["text"])
                return True
        
        # Check feedback buttons
        if self.hint_shown:
            for btn in self.feedback_buttons:
                if btn["rect"].collidepoint(pos):
                    self.process_feedback(btn["value"], current_board_state)
                    return True
                    
        return False 