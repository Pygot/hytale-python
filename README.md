# hytale-python
Who likes java, nobody right? Python is better. Here, use this, it might be more annoying, but it's python!

### To compile follow these steps:
1. Replace ```libs/HytaleServer.jar``` mock with the actual **HytaleServer.jar**
2. Build shadowJar

This mod exposes ```this``` as __plugin__ and ```init``` as __init__. You can use ```runOnMain()``` to run tasks from the main thread. The mod will also create ```scripts/``` directory at startup, you can copy the ```scripts_example``` content into it.

### Don't forget that this is Jython, so you can use only Python2 not Python3. If you need Python3, consider checking out [JyNi](https://github.com/Stewori/JyNI)!

---

# robot - mod

> This mod was created, so I can participate in the first ever Hytale Modjam, good luck my opponents! See more here: [hytalemodjam.com](https://hytalemodjam.com/)

This "mod", which uses jython and my hytale-python mod, is a mod that adds an NPC named Robot to your server. The Robot will be happy to help you survive, or will be happy to help you kill you.

### How to play with Robot?
1. Follow the __hytale-python__ compilation instructions to obtain ```.jar```
2. Copy the ```robot/``` __content__ to ```scripts/```
3. Restart the server or reload the hytale-python plugin

### Why Jython?
Because I don't know Java! Lol - @Pygot 02.02.2026

### TODO LIST (Important TOP - Less Important BOTTOM):
- [x] Create model for Robot
- [ ] Create Robot AI logic
- [ ] Create Documentation
- [ ] Give Robot a better name
- [ ] Record gameplay
- [ ] Story-telling about the project as another video
