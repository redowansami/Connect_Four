# Connect Four Game

## Description
This is an implementation of the Connect Four game with an AI opponent using Python and Pygame. The AI uses the Minimax algorithm with alpha-beta pruning and an evaluation function for strategic play. The game features a graphical user interface and includes an early stopping mechanism based on time limits. The board fills from the bottom up, as per standard Connect Four rules.

## Requirements
- Python 3.8+
- Pygame (`pip install pygame`)

## Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd connect-four
```
2. Install dependencies:
```bash
pip install pygame
```
3. Run the game:
```bash
python main.py
```

## How to Play
- The human player (Red) goes first, clicking a column to drop a token.
- The AI (Yellow) responds automatically.
- The goal is to connect four tokens horizontally, vertically, or diagonally.
- Close the window to exit the game.

## Features
- **Minimax Algorithm**: Used to select the best move for the AI.
- **Alpha-Beta Pruning**: Optimizes the search by pruning unnecessary branches.
- **Evaluation Function**: Scores board positions based on potential wins and strategic positions.
- **Early Stopping**: Limits AI thinking time to 2 seconds per move.
- **Graphical Interface**: Built with Pygame, showing a grid and colored tokens.

## Project Structure
- `board.py`: Board creation, piece placement, and win condition logic.
- `minimaxAI.py`: AI logic including minimax, alpha-beta pruning, and evaluation function.
- `main.py`: Game loop and Pygame user interface.
- `README.md`: Project documentation.

## Git Repository
The project is maintained in a Git repository. To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Description"`).
4. Push to the branch (`git push origin feature-name`).
5. Create a pull request.

## License
MIT License
