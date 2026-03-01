# Report for assignment 4

## Project

**Name:** Sir Lancebot

**URL:** https://github.com/python-discord/sir-lancebot

Sir Lancebot is a Discord bot developed for the Python Discord server. The bot is intended as a fun introduction to open source contribution and includes a wide variety of features, including a list of games where players are awarded points for winning.
<br>
## Onboarding experience

We chose a new project this time. The onboarding experience was generally easier for this project, as it is intended to be beginner-friendly and is therefore very well documented with detailed instructions on how to set up the environment. The project also includes a Dockerfile, which simplifies the setup process further by avoiding the installation of dependencies on each device. The onboarding instructions also recommended using Gitpod to edit and test the bot, which automatically installs the correct dependencies and Python version. However, it requires you to create an account and will sometimes prompt the user to complete a $1 payment (which will be immediately refunded) as a form of CAPTCHA test.

The previous project we worked on, NewPipe, was less structured when it comes to documentation and required the installation of Android Studio and manual setting of an environment variable in order to be run. NewPipe was also significantly larger than Sir Lancebot (>13 times larger in lines of code, and >34 times as many files), which made the overall structure more challenging to comprehend and caused memory-related issues on some devices.
<br>
## Effort spent

The table below shows how much time each team member spent on different parts of the assignment.

|                                              | Ammar Alzeno | Jens Cancio | Anna Remmare | Amanda Henrion Eskeus | Nora Wennerström |
| -------------------------------------------- | ------------ | ----------- | ------------ | --------------------- | ---------------- |
| **1. plenary discussions/meetings**          | 4h           | 4h          | 4h           | 4h                    | 4h               |
| **2. discussions within parts of the group** | 1h           | 1h          | 2h           | 1h                    | 1h               |
| **3. reading documentation**                 | 2h           | 1h          | 2h           | 3h                    | 3h               |
| **4. configuration and setup**               | 2h           | 1h          | 1h           | 2h                    | 1h               |
| **5. analyzing code/output**                 | 1h           | 4h          | 6h           | 0h                    | 6h               |
| **6. writing documentation**                 | 1h           | 0.5h        | 3h           | 4h                    | 8h               |
| **7. writing code**                          | 7h           | 8h          | 5h           | 3h                    | 0h               |
| **8. running code**                          | 1h           | 1.5h        | 2h           | 2min                  | 0h               |
| **Total**                                    | **19h**      | **21h**     | **25h**      | **~17h**              | **23h**          |

### Notes
**Ammar:** 
    4. Took some time to set up the bot locally for testing as well.
    6. Estimate. Mostly just the comments for all functions in the code.
**Anna:** 
    3. project, pytest, task.pdf
    4. Python 3.13, venv, pytest, .env.test / bot startup, uv: ~45 min --> had a hard time getting the correct versions
    5. leaderboard.py, cog, scoring; designing tests
    6. report_test_section.md, test log headers
    7. test_leaderboard_utils.py, test_scoring_rules.py
    8. pytest, bot startup, fault-injection runs, capturing logs
**Amanda:** 
    4. Updating Python, installing UV, Gitpod, learning about setting up a Discord bot, looking for and setting environment variables.
    6. Requirements + UML
    7. UML
**Nora:** 
    4. Installing docker-compose and solving related issues.
    6. All parts of the report except requirements, UML and architectural overview.
<br>
## Overview of issue(s) and work done.

Title: Global Leaderboard

URL: https://github.com/python-discord/sir-lancebot/issues/627

The issue describes an added feature consisting of a global leaderboard where points from each game are normalized and added to a total score for each user. Some games (e.g. coinflip) are easier to win than others (e.g. minesweeper) and will therefore give less points on the global leaderboard.

<!--Scope (functionality and code affected).-->
The new feature can be implemented without major changes to existing files. The only necessary changes are the addition of constants representing the normalized number of points for each game, adjustments to printed messages, as well as a line of code which adds the points to the user's global sum when they win a game. This also requires an instance of the project's Bot class to be passed to the function for adding points, since it will be used to save the state.

Some files may require slightly larger edits due to the game's point system being more complicated. This can for example be seen in [duck_game.py](bot/exts/fun/duck_game.py), where the top three players all get points added to the leaderboard, or in [minesweeper.py](bot/exts/fun/minesweeper.py), where the amount of points awarded depends on the difficulty level of the game.

The leaderboard is implemented in the new file [leaderboard.py](bot/exts/fun/leaderboard.py), using functions defined in [utils/leaderboard.py](bot/utils/leaderboard.py). This adds the functionality described in the following section, along with the additional pagination described briefly in the final section of the report. More information about how the added class works can be found in section "UML class diagram and its description".
<br>
## Requirements for the new feature

<!--Optional (point 3): trace tests to requirements.-->

**Overall goal**
Combine the leader-boards from all the existing games into a global leaderboard.

**Functional requirements**
The new feature should satisfy the following functional requirements:

- **FR1 - Global leaderboard:** Players should be able to see a global leaderboard using a certain command. This leaderboard should display each player's earned points since it was initiated or since it was last cleared.
    - **FR1.1 - Clear permission:** Only admins should be able to clear the global leaderboard.
    - **FR1.2 - Automatic updates:** The global leaderboard should automatically update a player's points as soon as they finish playing a game that make use of a leaderboard. add_point and remove_points utils functions would be helpful to implement and use for this
    - **FR1.3 - Daily limit:** There is a limit for how many points a player can earn per day. After said limit is reached, players can still play games but no more points are added until the daily global leaderboard is reset.
<br>

- **FR2 - Daily leaderboard:** Players should be able to see a daily global leaderboard using a certain command. This leaderboard should display each player's earned points from the current day.
    - **FR2.1 - Daily reset:** The daily global leaderboard should reset automatically at the start of each day.
    - **FR2.2 - Automatic updates:** The daily global leaderboard should automatically update a player's points as soon as they finish playing a game that make use of a leaderboard. add_point and remove_points utils functions would be helpful to implement and use for this
    - **FR2.3 - Isolate update effects:** Changes made to the daily global leaderboard should not influence players' number of points in the global leaderboard or any game-specific leaderboard, meaning the daily reset should not remove any points from other leaderboards
    - **FR2.4 - Daily limit:** There is a limit for how many points a player can earn per day. After said limit is reached, players can still play games but no more points are added until the daily global leaderboard is reset.
<br>

- **FR3 - Games:** Points in the global leaderboard and daily global leaderboard are normalized points/coins from each of the following games' leader-boards:
    - **FR3.1: Battleship**
    - **FR3.2: Coinflip**
    - **FR3.3: Connect 4**
    - **FR3.4: Snakes**
    - **FR3.5: Minesweeper**
    - **FR3.6: Tic Tac Toe**
    - **FR3.7: Trivia Quiz**
    - **FR3.8: Easter Riddle**
    - **FR3.9: Egg Head Quiz**
    - **FR3.10: Hangman**
    - **FR3.11: Rock Paper Scissors**
    - **FR3.12: Anagram**
    - **FR3.13: Duck Duck Goose**


**Non-functional requirements**
The new feature should satisfy the following non-functional requirements:

- **NFR1 - Aesthetics:** The displays of the global leaderboard and daily global leaderboard should be easily understandable and pretty


**Optional (point 3): trace tests to requirements.** <!--explain where no tests are needed!-->

- **FR1.1 - Clear permission:**
<!--Only admins should be able to clear the global leaderboard-->
No tests were added for this requirement.

- **FR1.2 - Automatic updates:**
The addition of points to the total is tested by methods test_add_points_increases_score(), test_add_points_increments_when_user_already_in_cache() and test_add_points_zero_is_no_op() in [LeaderboardUtilsTests](tests/test_leaderboard_utils.py).
The method test_coinflip_win_calls_add_points_with_correct_value() in [ScoringRulesTests](tests/test_scoring_rules.py) tests that the correct number of points is added automatically after a win in coinflip.

- **FR1.3 - Daily limit:**
The daily cap is tested by method test_add_points_daily_cap_no_add() in [LeaderboardUtilsTests](tests/test_leaderboard_utils.py). <!--(players can still play games?)-->
<br>

- **FR2.1 - Daily reset:**
This functionality is not tested, but it should work as intended since the same method is used in previously accepted and integrated parts of the project.

- **FR2.2 - Automatic updates:**
This requirement does not require further testing, as the daily leaderboard is updated in the same way as the code which is already tested for FR1.2.

- **FR2.3 - Isolate update effects:**
No tests were added to make sure that this requirement is fulfilled.


- **FR2.4 - Daily limit:**
See FR1.3. 
<br>

- **FR3:**
The same function is called in the same way in all games, so only one (coinflip) is tested by method test_coinflip_win_calls_add_points_with_correct_value() in [ScoringRulesTests](tests/test_scoring_rules.py).
<br>
## Code changes

### Patch

Git command to show changes:

```
git remote add upstream https://github.com/python-discord/sir-lancebot.git
git fetch upstream
git diff upstream/main..feat/global-leaderboard
```
<br>

**Optional (point 4): the patch is clean.**
The patch does not comment out any code and does not change the original formatting. The only changes made are those necessary in order to fulfill the desired functionality of the leaderboard. No extraneous output is produced.
<br>

**Optional (point 5): considered for acceptance (passes all automated checks).**
A pull request has been opened, and the solution is being discussed here:
https://github.com/python-discord/sir-lancebot/pull/1730

**Note:** The project does not use a testing framework, so the patch submitted for acceptance does not include the test files.
<br>
## Test results

<!--Overall results with link to a copy or excerpt of the logs (before/after
refactoring).-->
The 16 added tests all pass after adding the new feature. The leaderboard has 100% branch coverage, and the game "coinflip" has 61% coverage. All tests call functions which were added for the new feature.

**Detailed output:**
[test_log_before.txt](docs/test_log_before.txt)
[test_log_after.txt](docs/test_log_after.txt)
[test_log_fail.txt](docs/test_log_fail.txt)
<br>
## UML class diagram and its description

![UML class diagram](uml/global-leaderboard-uml.png)

The UML class diagram above illustrates the main classes involved in the global leaderboard system, tracking points earned by users across different games and displaying rankings using Discord commands.

The central class is Leaderboard, which is implemented as a Discord Cog. It handles all leaderboard-related commands such as displaying rankings, showing user scores, and clearing the leaderboard using helper methods. The leaderboard data is stored using RedisCache, which provides persistent storage for the user points. 

The ConfirmClear class is a discord.ui.View used to display interactive buttons that allow administrators to confirm or cancel clearing the leaderboard.

Pagination of leaderboard results is handled by the LinePaginator utility class, which splits large result sets into multiple Discord messages.

Game classes contribute points to the leaderboard when a game ends. These classes interact indirectly with the leaderboard system through leaderboard utility functions. In order to avoid confusion, several game classes that had the same name have been renamed in the UML diagram to match the game they are representing. This change regards BattleshipGame, ConnectFourGame, MinesweeperGame, and TicTacToeGame. 
<br>
### Key changes/classes affected
<!--The architecture and purpose of the system are presented in an overview of about 1–1.5 pages; consider
using a diagram. Note: If you manage to improve on existing documentation or fill a gap in the project
here, please consider making your documentation available to the project; they may be grateful for it!-->
The only new classes are Leaderboard and ConfirmClear. All the game classes were otherwise present at the start of the project. They have been affected in the sense that they were refactored to also record points for the global leaderboard at the end of a game session. RedisCache and LinePaginator have not been affected other than for the fact they are now used by Leaderboard.

**Optional (point 1): Architectural overview.**

The leaderboard system follows a modular architecture, where functionality is separated into different components:
- Cogs for handling command logic
- Utility modules for management and calculations
- Cache systems for data to be persisted (RedisCache in this case)
- Game modules for awarding points

This separation seems to be quite typical for Discord bots. It improves maintainability and allows new games to easily integrate with the global leaderboard system without modifying existing leaderboard logic.

**Optional (point 2): relation to design pattern(s).**
<!--Updates in the source are put into context with the overall software architecture and discussed, relating
them to design patterns and/or refactoring patterns.-->

The leaderboard system makes use of some patterns similar to those described by the Gang of Four.

The most obvious use of a design pattern is that of the Discord Cog, which utilizes the **Command pattern**. The Command pattern is used throughout the project by the Discord command framework, where user commands trigger specific methods within the Leaderboard cog. The same pattern is used for the newly added leaderboard as well, making it familiar for others working on the project.

The **Model–View–Controller** (MVC) design pattern is loosely followed. For the global leaderboard, the data (which corresponds to the model) is stored using RedisCache, and the command logic is grouped in the Leaderboard class. As for the view, Discord messages are paginated using LinePaginator before being displayed to users with embeds. For the different games, the separation of the three parts varies, most likely depending on who made the contribution.

The class ConfirmClear overrides some behavior of ui.View, matching the **Template-Method pattern**. This pattern is characterized by a base class defining an algorithm and a child class overriding parts of it. This same idea can also be found in other parts of the project.

The shared RedisCache also works similarly to what is described in the **Singleton pattern**, but technically allows for multiple instantiations and uncontrolled access to the state.

<br>

## Overall experience

<!--What are your main take-aways from this project? What did you learn?-->
The contrast between this project and the previous one shows the importance of a structured repository and detailed documentation. Allowing anyone to create an issue also clearly requires some moderation in order to keep the repository clean and make things simpler for those who want to contribute. NewPipe having 1,327 open issues, most of which describe bugs experienced by individual users when using the app, is quite unattractive for people looking to contribute, as it increases the risk for duplicate or overlapping issues that might get assigned to different people. In the future, it might be a good idea to take a look at things like documentation and open issues or pull requests before deciding to contribute to a project, thus hopefully avoiding the more difficult onboarding processes and other issues that might arise from ambiguous requirements or an inactive community.

The experience gained in this assignment (and the previous one) also helped us in realizing that you don't need to be an expert with years of experience in order to be able to make meaningful contributions to open-source software. Many projects have unsolved issues for new features, bug fixes or refactors that we as students possess the skill to solve. There are also many projects (like Sir Lancebot) which are intented as a beginner-friendly introduction to open-source contribution. In the process of looking for projects for these assignments, we have also found many other interesting projects that we might want to try working on in the future.

**How did you grow as a team, using the Essence standard to evaluate yourself?**
We believe that we are still in the "working well" stage of the Essence standard for way of working. Since issues cannot be created in a fork on GitHub, the way of working had to be adjusted slightly for this assignment when it comes to version control practices. Still, commits were created with messages that follow the same standards as previously, without having to reestablish the guidelines. We kept the same general plan as for the previous assignments, meaning that we start with a meeting where we go through the instructions, divide the work and plan ahead. Normally, some students' tasks will depend on others being finished first, so these relationships are also noted at the first meeting and addressed in the planning. This time, we added another meeting where the result of the first task (the leaderboard) is presented before the rest of the group members start working on their parts. A similar meeting was also conducted when the code was finished and only the report remained to be written. This slight increase in communication cut down the time each group member had to spend on familiarizing themselves with the others' work, and started the conversation around the more ambiguous parts of the assignment at an earlier point than previously. We consider this further proof that our way of working has evolved in the *working well* stage.

**Checklist**
| State                   | Checklist |
|-------------------------|-----------|
| **Principles Established** | [x] Principles and constraints are committed to by the team. <br> [x] Principles and constraints are agreed to by the stakeholders. <br> [x] The tool needs of the work and its stakeholders are agreed. <br> [x] A recommendation for the approach to be taken is available. <br> [x] The context within which the team will operate is understood. <br> [x] The constraints that apply to the selection, acquisition, and use of practices and tools are known. |
| **Foundation Established** | [x] The key practices and tools that form the foundation of the way-of-working are selected. <br> [x] Enough practices for work to start are agreed to by the team. <br> [x] All non-negotiable practices and tools have been identified. <br> [x] The gaps that exist between the practices and tools that are needed and the practices and tools that are available have been analyzed and understood. <br> [x] The capability gaps that exist between what is needed to execute the desired way of working and the capability levels of the team have been analyzed and understood. <br> [x] The selected practices and tools have been integrated to form a usable way-of-working. |
| **In Use** | [x] The practices and tools are being used to do real work. <br> [x] The use of the practices and tools selected are regularly inspected. <br> [x] The practices and tools are being adapted to the team’s context. <br> [x] The use of the practices and tools is supported by the team. <br> [x] Procedures are in place to handle feedback on the team’s way of working. <br> [x] The practices and tools support team communication and collaboration. |
| **In Place** | [x] The practices and tools are being used by the whole team to perform their work. <br> [x] All team members have access to the practices and tools required to do their work. <br> [ ] The whole team is involved in the inspection and adaptation of the way-of-working. |
| **Working Well** | [x] Team members are making progress as planned by using and adapting the way-of working to suit their current context. <br> [x] The team naturally applies the practices without thinking about them. <br> [x] The tools naturally support the way that the team works. <br> [x] The team continually tunes their use of the practices and tools. |
| **Retired** | [ ] The team's way of working is no longer being used. <br> [x] Lessons learned are shared for future use. |

**Optional (point 6): How would you put your work in context with best software engineering practice?**
- **Stakeholders:**

In this case, the stakeholders are the Python Discord community, specifically those active in reviewing issues and pull request on the Sir Lancebot repository. At the time of writing this, the relationship with the stakeholders is in the *involved* stage, as they have given feedback, but it still isn't clear whether the updates to the code are enough to satisfy their requirements.

- **Opportunity:**

The opportunity alpha is currently somewhere between *viable* and *addressed*. The stakeholders seem satisfied with the approach to address the opportunity, but it is still unclear whether they are happy with the concrete implementation of the system. The opportunity cannot be described as "profitable", but this seems irrelevant for a project such as this one regardless.

- **Requirements:**

The requirements are fulfilled. Considering that the feature is of a smaller scope with relatively simple requirements, it makes sense that this alpha would be at the final stage.

- **Software System:**

The software system is at least at the *usable* stage, but would increase to the *operational* stage if the pull request is accepted.

- **Team:**

Depending on one's interpretation of the definitions, the team could either be at the *collaborating* or the *performing* stage. Not all members know each other beyond the scope of the course, and it happens that we don't deliver on commitments we have made, specifically when it comes to self-imposed deadlines. Despite this, we have always been able to present the work on time at the intended level, and we address issues openly and honestly. 

- **Work:**

Once the resulting system is accepted, the work will be *concluded*.

**Optional (point 7): Is there something special you want to mention here?**
<!--You have done something extraordinary that exceeds the scope of the assignment, and which you can
be proud of.-->
The pagination functionality is a nice way of giving users access to more information in a cleaner way, and will be familiar to users of the bot since the same functionality is implemented for the help command as well. This was not requested in the issue, but was added anyway to improve the user experience. The same goes for the addition of a daily leaderboard that gets cleared at midnight. Since other parts of the bot use the same update mechanism, the new function will be programmatically familiar and easy to understand for other contributors.

