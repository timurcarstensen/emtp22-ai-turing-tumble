# European Master Team Project - AI Turing Tumble

> This repository holds the code that was developed during the European Master Team Project
> in the spring semester of 2022 (EMTP 22). The project was supervised by
> [Dr. Christian Bartelt](https://www.uni-mannheim.de/en/ines/about-us/researchers/dr-christian-bartelt/) and
> [Jannik Brinkmann](https://www.linkedin.com/in/brinkmann-jannik/). The project team was
> composed of students from the [Babeș-Bolyai University](https://www.ubbcluj.ro/en/)
> in Cluj-Napoca, Romania, and the [University of Mannheim](https://www.uni-mannheim.de/), Germany.

## Introduction

In the game Turing Tumble, players construct mechanical computers that use the flow of marbles along a board to solve
logic problems. As the board and its parts are Turing complete, which means that they can be used to express any
mathematical function, an intelligent agent taught to solve a Turing Tumble challenge essentially learns how to write
code according to a given specification.

Following this logic, we taught an agent how to write a simple programme according to a minimal specification, using
an abstracted version of the Turing Tumble board as reinforcement learning training environment. This is related to
the emerging field of programme synthesis, as is for example applied in
[GitHub’s CoPilot](https://github.com/features/copilot).

## Participants

### Babeș-Bolyai University

* [Tudor Esan](https://github.com/TudorEsan) - B.Sc. Computer Science
* [Raluca Diana Chis](https://github.com/RalucaChis) - M.Sc. Applied Computational Intelligence

### University of Mannheim

* [Roman Hess](https://github.com/romanhess98) - M.Sc. Data Science
* [Timur Carstensen](https://github.com/timurcarstensen) - M.Sc. Data Science
* [Julie Naegelen](https://github.com/jnaeg) - M.Sc. Data Science
* [Tobias Sesterhenn](https://github.com/Tsesterh) - M.Sc. Data Science

## Contents of this repository

The project directory is organised in the following way:

| Path                      | Role                                         |
|---------------------------|----------------------------------------------|
| `docs/`                   | Supporting material to document the project  |
| `reinforcement_learning/` | Everything related to Reinforcement Learning |
| `src/`                    | Java sources                                 |
| `ttsim/`                  | Source Code of the Turing Tumble Simulator   |

## Weights & Biases (wandb)
We used [Weights & Biases](https://wandb.ai/) to log the results of our training: 
1. [Reinforcement Learning](https://wandb.ai/mtp-ai-board-game-engine/ray-tune-bugbit)
2. [Pretraining](https://wandb.ai/mtp-ai-board-game-engine/Pretraining)
3. [Connect Four](https://wandb.ai/mtp-ai-board-game-engine/connect-four)

## Credits

We used third-party software to implement the project. Namely:

- **BugPlus** - [Dr. Christian Bartelt](https://www.uni-mannheim.de/en/ines/about-us/researchers/dr-christian-bartelt/)
- **Turing Tumble Simulator** - [Jesse Crossen](https://github.com/jessecrossen/ttsim)

## Final Project Presentation

Link to video:
[![Final Project Presentation Video](https://img.youtube.com/vi/w501gf2MLFM/0.jpg)](https://www.youtube.com/watch?v=w501gf2MLFM)

