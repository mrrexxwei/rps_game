import cv2
import mediapipe as mp
import random
import time

class RockPaperScissors:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.choices = ['Rock', 'Paper', 'Scissors']
        self.player_score = 0
        self.computer_score = 0
        self.game_state = 'waiting'  # waiting, countdown, result
        self.countdown_start = 0
        self.result_start = 0
        self.player_choice = None
        self.computer_choice = None
        self.winner = None
        
    def count_fingers(self, hand_landmarks):
        """Count extended fingers to determine gesture"""
        fingers = []
        
        # Thumb (different logic - check if tip is left/right of IP joint)
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # Other fingers (check if tip is above PIP joint)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return sum(fingers)
    
    def detect_gesture(self, hand_landmarks):
        """Detect Rock, Paper, or Scissors gesture"""
        finger_count = self.count_fingers(hand_landmarks)
        
        if finger_count == 0:
            return 'Rock'
        elif finger_count >= 4:
            return 'Paper'
        elif finger_count == 2:
            return 'Scissors'
        return None
    
    def determine_winner(self, player, computer):
        """Determine the winner of the round"""
        if player == computer:
            return 'Tie'
        elif (player == 'Rock' and computer == 'Scissors') or \
             (player == 'Paper' and computer == 'Rock') or \
             (player == 'Scissors' and computer == 'Paper'):
            return 'Player'
        else:
            return 'Computer'
    
    def run(self):
        """Main game loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("Rock-Paper-Scissors Game Started!")
        print("Press 'SPACE' to start a round")
        print("Press 'Q' to quit")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            current_time = time.time()
            
            # Draw hand landmarks
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                    
                    # Game logic based on state
                    if self.game_state == 'countdown':
                        gesture = self.detect_gesture(hand_landmarks)
                        
                        # Check countdown
                        elapsed = current_time - self.countdown_start
                        if elapsed >= 3:
                            # Capture player choice
                            self.player_choice = gesture if gesture else 'Rock'
                            self.computer_choice = random.choice(self.choices)
                            self.winner = self.determine_winner(
                                self.player_choice, self.computer_choice
                            )
                            
                            # Update scores
                            if self.winner == 'Player':
                                self.player_score += 1
                            elif self.winner == 'Computer':
                                self.computer_score += 1
                            
                            self.game_state = 'result'
                            self.result_start = current_time
            
            # Draw UI
            self.draw_ui(frame, current_time)
            
            cv2.imshow('Rock-Paper-Scissors', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' ') and self.game_state == 'waiting':
                self.game_state = 'countdown'
                self.countdown_start = current_time
            elif key == ord('r'):
                self.player_score = 0
                self.computer_score = 0
                self.game_state = 'waiting'
        
        cap.release()
        cv2.destroyAllWindows()
    
    def draw_ui(self, frame, current_time):
        """Draw game UI on frame"""
        h, w = frame.shape[:2]
        
        # Draw scores
        cv2.putText(frame, f"Player: {self.player_score}", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Computer: {self.computer_score}", (w - 250, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        if self.game_state == 'waiting':
            cv2.putText(frame, "Press SPACE to start!", (w//2 - 200, h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, "Show your gesture when countdown ends", 
                        (w//2 - 300, h//2 + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        elif self.game_state == 'countdown':
            elapsed = current_time - self.countdown_start
            countdown = 3 - int(elapsed)
            if countdown > 0:
                cv2.putText(frame, str(countdown), (w//2 - 50, h//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 8)
            else:
                cv2.putText(frame, "SHOW!", (w//2 - 100, h//2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        
        elif self.game_state == 'result':
            # Show choices
            cv2.putText(frame, f"You: {self.player_choice}", (50, h - 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.putText(frame, f"Computer: {self.computer_choice}", 
                        (50, h - 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            
            # Show winner
            if self.winner == 'Tie':
                text = "It's a Tie!"
                color = (255, 255, 0)
            elif self.winner == 'Player':
                text = "You Win!"
                color = (0, 255, 0)
            else:
                text = "Computer Wins!"
                color = (0, 0, 255)
            
            cv2.putText(frame, text, (w//2 - 150, h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)
            
            # Return to waiting after 3 seconds
            if current_time - self.result_start >= 3:
                self.game_state = 'waiting'
        
        # Instructions
        cv2.putText(frame, "Q: Quit | SPACE: Start | R: Reset", 
                    (20, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

if __name__ == "__main__":
    game = RockPaperScissors()
    game.run()