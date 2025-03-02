Cheat at the popular game AnimeMusicQuiz

## Overview

This script uses a virtual audio cable program (a program that captures the output of a device and routes it to a virtual input device) record the output suing ffmpeg. 
Then, it uses [ShazamIO](https://github.com/shazamio/ShazamIO) to identify the song name. Subsequently, it utilizes the "animethemes" API to retrieve the anime show name. Finally, the script uses [Selenium](https://www.selenium.dev/) to enter the anime show name into the game and saves a song-name to anime-name mapping for future use.

## Setup and How to Use

1.  Install a virtual audio cable program (any program that functions similarly, such as [Voicemeeter](https://vb-audio.com/Voicemeeter/index.htm)).
2.  Download FFmpeg and place the executable (exe) file in the same directory as the script.
3.  Install the required Python libraries.
4.  Open a Python console and import the script:

```python
import amq_cheat
```
This will open a browser window to the AnimeMusicQuiz website.   

5.  After signing in and starting a game, run the command:
```Python
amq_cheat.play_game()
```
## Accuracy Rate
Initially, the accuracy rate is quite low, around 20%, primarily due to the translation from song name to anime name. However, after playing enough games, the accuracy rate will improve to approximately 60%.