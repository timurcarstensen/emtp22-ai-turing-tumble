/**
 * Implementation of the ConnectFour Environment.
 */

package connectfour;

import java.util.*;
import java.util.concurrent.ThreadLocalRandom;


public class ConnectFour {


    private final int WIDTH = 7;
    private final int HEIGHT = 6;
    private boolean done = false;
    private int winner = 0;
    private String game_mode = "no_interaction";

    private int[][] board = new int[HEIGHT][WIDTH];

    public ConnectFour() {
        this.reset();
    }

    public int[][] reset() {
        for (int i = 0; i < this.HEIGHT; i++) {
            for (int j = 0; j < this.WIDTH; j++) {
                this.board[i][j] = 0;
            }
        }
        this.done = false;
        return this.board;
    }

    public static void main(String[] args) {

    }

    public LinkedList<Object> selfplay_step(int action, int player) {
        int reward = 0;
//        unless the board is full...
        if (!boardFull()) {
//            if the action is valid...
            if (actionValid(action)) {
//                place the token at the indicated column for player 1 (i.e. the agent)
                placeToken(action, player);
//                if player 1 one won after the last move, set the reward to 1000
                if (checkWinner(this.board)[0] == 1) {
                    if (checkWinner(this.board)[1] == 2) {
                        reward = 50;
                    } else {
                        reward = 50;
                    }
                    this.done = true;
                    this.winner = 1;
//                else if player 2 now won, (which should not happen since player 2 has not made a move yet), set the reward to -1000
                } else if (checkWinner(this.board)[0] == 2) {
                    reward = -50;
                    this.done = true;
                    this.winner = 2;
//                else if none of them have won, sample a greedy action of player 2 to take and place it
                } else if (checkWinner(this.board)[0] == 0) {
                    if (boardFull()) {
                        this.done = true;
                        this.winner = 0;
                        reward = -10;
//                    if player 1 and 2 have made their move and none of them have won, let the reward for this action (by player) be -1;
                    } else {
                        reward = -1;
                    }
                }
//            if the action (by player 1) is invalid, let the reward be -200
            } else {
                reward = -1000;
                this.done = true;
                this.winner = 2;
            }
//            if the board is full and none of them have won, the reward will be -1000;
        } else {
            this.done = true;
            this.winner = 0;
            reward = -10;
        }

        LinkedList<Object> output = new LinkedList<Object>();
        output.add(this.board);
        output.add(reward);
        output.add(this.done);
        output.add(null);
        System.out.println("EOS");
        return output;
    }

    public LinkedList<Object> step(int action, int player) {
        int reward = 0;
        LinkedList<Object> output = new LinkedList<Object>();

        if (!boardFull()) {
            if (actionValid(action)) {
                placeToken(action, player);
                int winner = checkWinner(this.board)[0];
                if (winner == 1 || winner == 2) {
                    output.add(this.board);
                    output.add(reward);
                    output.add(true);
                    output.add(null);
                    output.add(winner);
                    return output;
                } else if (winner == 0) {
                    output.add(this.board);
                    output.add(reward);
                    output.add(false);
                    output.add(null);
                    output.add(winner);
                    return output;
                }

            }
        }
        output.add(this.board);
        output.add(0); // reward
        output.add(true); // done
        output.add(null);
        output.add(0);
        return output;
    }

    public LinkedList<Object> interactive_step(int agentAction) {
        int reward = 0;
//        unless the board is full...
        if (!boardFull()) {
//            if the action is valid...
            if (actionValid(agentAction)) {
//                place the token at the indicated column for player 1 (i.e. the agent)
                placeToken(agentAction, 1);
//                if player 1 one after the last move, set the reward to 1000
                if (checkWinner(this.board)[0] == 1) {
                    if (checkWinner(this.board)[1] == 2) {
                        reward = 50;
                    } else {
                        reward = 50;
                    }
                    this.winner = 1;
                    this.done = true;
//                else if player 2 now won, (which should not happen since player 2 has not made a move yet), set the reward to -1000
                } else if (checkWinner(this.board)[0] == 2) {
                    reward = -50;
                    this.winner = 2;
                    this.done = true;
//                else if none of them have won, sample a random action of player 2 to take and place it
                } else if (checkWinner(this.board)[0] == 0) {
//                    if after player 2 has made their move, the board is either full or player 2 won, set the reward to -1000
                    if (checkWinner(this.board)[0] == 2) {
                        this.done = true;
                        this.winner = 2;
                        reward = -50;
                    } else if (boardFull()) {
                        this.done = true;
                        this.winner = 0;
                        reward = -50;
//                   if player 1 and 2 have made their move and none of them have won, let the reward for this action (by player) be -1;
                    } else {
                        reward = -1;
                    }
                }
//            if the action (by player 1) is invalid, let the reward be -200
            } else {
                reward = -10;
                this.winner = 0;
                this.done = true;
            }
//            if the board is full and none of them have won, the reward will be -1000;
        } else {
            this.done = true;
            this.winner = 0;
            reward = -10;
        }

        LinkedList<Object> output = new LinkedList<Object>();
        output.add(this.board);
        output.add(reward);
        output.add(this.done);
        output.add(null);
        return output;
    }

    public LinkedList<Object> step(int action) {
        int reward = 0;
//        unless the board is full...
        if (!boardFull()) {
//            if the action is valid...
            if (actionValid(action)) {
//                place the token at the indicated column for player 1 (i.e. the agent)
                placeToken(action, 1);
//                if player 1 one won after the last move, set the reward to 1000
                if (checkWinner(this.board)[0] == 1) {
                    if (checkWinner(this.board)[1] == 2) {
                        reward = 50;
                    } else {
                        reward = 50;
                    }
                    this.done = true;
                    this.winner = 1;
//                else if player 2 now won, (which should not happen since player 2 has not made a move yet), set the reward to -1000
                } else if (checkWinner(this.board)[0] == 2) {
                    reward = -50;
                    this.done = true;
                    this.winner = 2;
//                else if none of them have won, sample a greedy action of player 2 to take and place it
                } else if (checkWinner(this.board)[0] == 0) {

                    greedyAction(2);
//                    if after player 2 has made their move, the board is either full or player 2 won, set the reward to -1000
                    if (checkWinner(this.board)[0] == 2) {
                        this.done = true;
                        this.winner = 2;
                        reward = -50;
                    } else if (boardFull()) {
                        this.done = true;
                        this.winner = 0;
                        reward = -10;
//                    if player 1 and 2 have made their move and none of them have won, let the reward for this action (by player) be -1;
                    } else {
                        reward = -1;
                    }
                }
//            if the action (by player 1) is invalid, let the reward be -200
            } else {
                reward = -1000;
                this.done = true;
                this.winner = 2;
            }
//            if the board is full and none of them have won, the reward will be -1000;
        } else {
            this.done = true;
            this.winner = 0;
            reward = -10;
        }

        LinkedList<Object> output = new LinkedList<Object>();
        output.add(this.board);
        output.add(reward);
        output.add(this.done);
        output.add(null);
        output.add(this.winner);
        return output;
    }

    private int sampleRandomAction() {
        return ThreadLocalRandom.current().nextInt(0, this.WIDTH);
    }

    private boolean boardFull() {
        for (int height = 0; height < this.HEIGHT; height++) {
            for (int width = 0; width < this.WIDTH; width++) {
                if (this.board[height][width] == 0) {
                    return false;
                }
            }
        }
        System.out.println("GAME OVER: The board is full");
        return true;
    }

    /***
     * @return true if the second player has not made a move yet
     */
 /*   private boolean noTokensFrom2ndPlayer() {
        for (int height = 0; height < this.HEIGHT; height++) {
            for (int width = 0; width < this.WIDTH; width++) {
                if (this.board[height][width] == 2) {
                    return false;
                }
            }
        }
        return true;
    }*/
    public void placeToken(int action, int player) {
        try {
            for (int i = this.HEIGHT - 1; i >= 0; i--) {
                if (this.board[i][action] == 0) {
                    this.board[i][action] = player;
                    break;
                }
            }
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Caught the array exception in placeToken()");
        }
    }

    private boolean actionValid(int action) {
        try {
            for (int i = this.HEIGHT - 1; i >= 0; i--) {
                if (this.board[i][action] == 0) {
                    return true;
                }
            }
            return false;
        } catch (ArrayIndexOutOfBoundsException exception) {
            //System.out.println("Caught ArrayIndexOutOfBoundsException");
            return false;
        }
    }

    private int[] checkWinner(int[][] board) {
        final int EMPTY_SLOT = 0;

        for (int r = 0; r < this.HEIGHT; r++) { // iterate rows, bottom to top
            for (int c = 0; c < this.WIDTH; c++) { // iterate columns, left to right
                int player = board[r][c];
                if (player == EMPTY_SLOT)
                    continue; // don't check empty slots

                if (c + 3 < WIDTH &&
                        player == board[r][c + 1] && // look right
                        player == board[r][c + 2] &&
                        player == board[r][c + 3])
                    return new int[]{player, 1};
                if (r + 3 < HEIGHT) {
                    if (player == board[r + 1][c] && // look up
                            player == board[r + 2][c] &&
                            player == board[r + 3][c])
                        return new int[]{player, 1};
                    if (c + 3 < WIDTH &&
                            player == board[r + 1][c + 1] && // look up & right
                            player == board[r + 2][c + 2] &&
                            player == board[r + 3][c + 3])
                        return new int[]{player, 2};
                    if (c - 3 >= 0 &&
                            player == board[r + 1][c - 1] && // look up & left
                            player == board[r + 2][c - 2] &&
                            player == board[r + 3][c - 3])
                        return new int[]{player, 2};
                }
            }
        }

        return new int[]{EMPTY_SLOT, 0}; // no winner found
    }

    public int[][] getState() {
        return this.board;
    }

    private void greedyAction(int playerID) {
        placeToken(getGreedyAction(playerID), playerID);
    }

    public int getGreedyAction(int playerID) {
        // if there are 3 pieces of the same colour in the same row, column or diagonal, place this piece next to them,..
        // ..in order to win or to stop the other player from winning

        float rand = new Random().nextFloat();
        if (rand < 0.1) {
            while (true) {
                int actionPlayer2 = sampleRandomAction();
                if (actionValid(actionPlayer2)) {
                    //placeToken(actionPlayer2, 2);
                    return actionPlayer2;
                }
            }
        }

        for (int r = 0; r < this.HEIGHT; r++) {
            for (int c = 0; c < this.WIDTH; c++) {
                int field = this.board[r][c];

                //make copy of the board
                if (checkValidPosition(r, c)) {
                    int[][] boardcopy = new int[this.HEIGHT][this.WIDTH];
                    for (int r2 = 0; r2 < this.HEIGHT; r2++) {
                        for (int c2 = 0; c2 < this.WIDTH; c2++) {
                            boardcopy[r2][c2] = this.board[r2][c2];
                        }
                    }

                    //can greedy agent win the game?
                    boardcopy[r][c] = playerID;
                    int winner = checkWinner(boardcopy)[0];
                    if (winner == playerID) {
                        //placeToken(c, 2);
                        return c;
                    }
                }
            }
        }
        for (int r = 0; r < this.HEIGHT; r++) {
            for (int c = 0; c < this.WIDTH; c++) {
                int field = this.board[r][c];

                //make copy of the board
                if (checkValidPosition(r, c)) {
                    int[][] boardcopy = new int[this.HEIGHT][this.WIDTH];
                    for (int r2 = 0; r2 < this.HEIGHT; r2++) {
                        for (int c2 = 0; c2 < this.WIDTH; c2++) {
                            boardcopy[r2][c2] = this.board[r2][c2];
                        }
                    }

                    //can agent win the game?
                    boardcopy[r][c] = playerID == 1 ? 2 : 1;
                    int winner = checkWinner(boardcopy)[0];
                    if (winner == (playerID == 1 ? 2 : 1)) {
                        //placeToken(c, 2);
                        return c;
                    }
                }
            }
        }

        int[] checkTrap = checkArisingTrap(playerID);
        if (checkTrap[2] != 0) {
            //int column = checkTrap[1];
            //int row = check2InARow(playerID)[0];
            //placeToken(column+check2InARow -2, 2);
            return checkTrap[1];
        }

        // same as above, but just for 2 pieces
        int[] check2InARow = check2InARow(playerID);
        if (check2InARow[2] != 0) {
            //int column = check2InARow[1];
            //int row = check2InARow[0];
            //placeToken(column+check2InARow -2, 2);
            return check2InARow[1];
        }


        // look for "alone" pieces
        int[] checkAlonePiece = checkAlonePiece(playerID);
        if (checkAlonePiece[2] != 0) {
            //int column = checkAlonePiece(playerID)[1];
            //placeToken(column+checkAlonePiece -2, 2);
            return checkAlonePiece[1];
        }

        // if none of the previous cases apply, make a random choice :(
        while (true) {
            int actionPlayer2 = sampleRandomAction();
            if (actionValid(actionPlayer2)) {
                //placeToken(actionPlayer2, 2);
                return actionPlayer2;
            }
        }
    }


    /**
     * this function checks if a token can be placed on an exact position
     * @param row: the row we want to place the token on
     * @param column: the column we want to place the token on
     * @return
     */
    private boolean checkValidPosition(int row, int column) {
        try {
            //check if field is empty
            if (this.board[row][column] == 0) {
                //check if we are in lowest row
                if (row == this.HEIGHT - 1) {
                    return true;
                }
                //check if there is another piece BELOW the position, s.t. a token can be placed exactly there
                if (this.board[row + 1][column] != 0) {
                    return true;
                }
            } else {
                return false;
            }
            return false;
            //check if positio is out of bounds
        } catch (ArrayIndexOutOfBoundsException exception) {
            //System.out.println("Caught ArrayIndexOutOfBoundsException");
            return false;
        }
    }

    /***
     * this function checks if there are 3 pieces of the same colour in the same row, column or diagonal
     * @return 1, place left
     *         2, place in current column
     *         5, place three to the right
     *         0, if no valid position
     */

    private int[] check3InARow() {
        for (int r = 0; r < this.HEIGHT; r++) { // iterate rows, bottom to top
            for (int c = 0; c < this.WIDTH; c++) { // iterate columns, left to right
                int player = this.board[r][c];
                if (player == 0)
                    continue; // don't check empty slots

                if (c + 2 < WIDTH &&
                        player == this.board[r][c + 1] && // look right
                        player == this.board[r][c + 2])
                    return new int[]{r, c, 1};
                if (r + 2 < HEIGHT) {
                    if (player == this.board[r + 1][c] && // look up
                            player == this.board[r + 2][c])
                        return new int[]{r, c, 2};
                    if (c + 2 < WIDTH &&
                            player == this.board[r + 1][c + 1] && // look up & right
                            player == this.board[r + 2][c + 2])
                        return new int[]{r, c, 3};
                    if (c - 2 >= 0 &&
                            player == this.board[r + 1][c - 1] && // look up & left
                            player == this.board[r + 2][c - 2])
                        return new int[]{r, c, 4};
                }
            }
        }
        return new int[]{0, 0, 0};
    }

    private int[] checkArisingTrap(int playerID) {
        /**
         * Checks if the greedy agent can possibly run into a trap:
         * this happens for the following scenario:
         * __OO__
         *
         */
        for (int r = 0; r < this.HEIGHT; r++) { // iterate rows, bottom to top
            for (int c = 0; c < this.WIDTH; c++) { // iterate columns, left to right
                int player = this.board[r][c];
                if (player == playerID || player == 0) //we want to look for the enemy
                    continue; // don't check empty slots

                if (c + 1 < WIDTH &&
                        player == this.board[r][c + 1]) {
                    if (checkValidPosition(r, c - 1) && checkValidPosition(r, c - 2) && checkValidPosition(r, c + 2)) {
                        return new int[]{r, c - 1, 1};
                    }
                    if (checkValidPosition(r, c + 2) && checkValidPosition(r, c - 1) && checkValidPosition(r, c + 3)) {
                        return new int[]{r, c + 2, 4};
                    }
                }
            }
        }
        return new int[]{0, 0, 0};
    }

    /***
     * this function checks if there are 2 pieces of the same colour in the same row or column
     * @return 1, place left
     *         2, place in current column
     *         4, place two to the right
     *         0, if no valid position
     */
    private int[] check2InARow(int playerID) {

        LinkedList<int[]> possibleMoves = new LinkedList<int[]>();
        for (int r = 0; r < this.HEIGHT; r++) { // iterate rows, bottom to top
            for (int c = 0; c < this.WIDTH; c++) { // iterate columns, left to right
                int player = this.board[r][c];
                if (player != playerID)
                    continue; // don't check empty slots

                if (c + 1 < WIDTH &&
                        player == this.board[r][c + 1]) {
                    if (checkValidPosition(r, c - 1)) {
                        possibleMoves.add(new int[]{r, c - 1, 1});
                    }
                    if (checkValidPosition(r, c + 2)) {
                        possibleMoves.add(new int[]{r, c + 2, 4});
                    }
                }

                if (r + 1 < HEIGHT && player == this.board[r + 1][c])
                    if (checkValidPosition(r - 1, c))
                        possibleMoves.add(new int[]{r, c, 2});
            }
        }
        if (possibleMoves.size() > 0) {
            Random rand = new Random();
            return possibleMoves.get(rand.nextInt(possibleMoves.size()));
        } else {
            return new int[]{0, 0, 0};
        }
    }

    /***
     * this function checks where next to an alone piece of the computer player another piece can be thrown
     * @return 1, if left
     *         2, if on top
     *         3, if right
     *         0, if nowhere
     */
    private int[] checkAlonePiece(int playerID) {
        LinkedList<int[]> possibleMoves = new LinkedList<int[]>();
        for (int r = 0; r < this.HEIGHT; r++) { // iterate rows, bottom to top
            for (int c = 0; c < this.WIDTH; c++) { // iterate columns, left to right
                int player = this.board[r][c];
                if (player != playerID)
                    continue; // don't check empty slots

                if (c - 1 > 0 && checkValidPosition(r, c - 1)) {

                    possibleMoves.add(new int[]{r, c - 1, 1});
                }
                if (c + 1 < WIDTH && checkValidPosition(r, c + 1))
                    possibleMoves.add(new int[]{r, c + 1, 3});
                if (r - 1 > 0 && checkValidPosition(r - 1, c))
                    possibleMoves.add(new int[]{r, c, 2});
            }
        }
        if (possibleMoves.size() > 0) {
            Random rand = new Random();
            return possibleMoves.get(rand.nextInt(possibleMoves.size()));
        } else {
            return new int[]{0, 0, 0};
        }
    }

    private int[] check3Enemy() {

        for (int r = 0; r < this.HEIGHT; r++) { // iterate rows, top to bottom
            for (int c = 0; c < this.WIDTH; c++) { // iterate columns, left to right
                int player = this.board[r][c];
                if (player != 1)
                    continue; // don't check empty spots or player 2

                if (c + 2 < WIDTH &&
                        player == this.board[r][c + 1] && // look right
                        player == this.board[r][c + 2])
                    return new int[]{r, c, 1};
                if (r + 2 < HEIGHT) {
                    if (player == this.board[r + 1][c] && // look up
                            player == this.board[r + 2][c])
                        return new int[]{r, c, 2};
                    if (c + 2 < WIDTH &&
                            player == this.board[r + 1][c + 1] && // look up & right
                            player == this.board[r + 2][c + 2])
                        return new int[]{r, c, 3};
                    if (c - 2 >= 0 &&
                            player == this.board[r + 1][c - 1] && // look up & left
                            player == this.board[r + 2][c - 2])
                        return new int[]{r, c, 4};
                }
            }
        }
        return new int[]{0, 0, 0};
    }

}
