
<div align="center">
    <img src="img/GoStreamLogoTitleRight.png">
    <h1>GOGAME DETECTION</h1>

<h3>Developed with the software and tools below</h3>
<p align="center">
    <img src="https://img.shields.io/badge/Jupyter-F37626.svg?style=flat-square&logo=Jupyter&logoColor=white" alt="Jupyter" />
    <img src="https://img.shields.io/badge/opencv--python-4.8.1.78-blue?style=flat-square&logo=opencv" alt="opencv-python" />
    <img src="https://img.shields.io/badge/scikit--learn-1.3.2-orange?style=flat-square&logo=scikit-learn" alt="scikit-learn" />
    <img src="https://img.shields.io/badge/sente-0.4.2-yellow?style=flat-square&logoColor=white" alt="sente" />
    <img src="https://img.shields.io/badge/ultralytics-8.0.231-brightgreen?style=flat-square&logoColor=white" alt="ultralytics" />
</p>
</div>

---

## Table of Contents
- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Modules](#modules)
- [Getting Started](#getting-started)
    - [Installation](#installation)
    - [Running GoGame-Detection](#running-gogame-detection)
- [Roadmap](#roadmap)
- [Acknowledgments](#acknowledgments)


---


## 📍 Overview

This project is dedicated to the development of a program capable of recognizing a game board, its stones and their respective positions within a go game context from a video stream.
The primary problem that our project tackles is the detection of the game setup at different angles without the need to set the camera at a fixed configuration. This capability allows for flexibility in changing the camera's angle or position, as well as adjusting the game board's placement during the course of the game. This stands as a distinctive feature compared to many existing solutions.


Key Highlights:
- **Real-time Game recognition:** Capable of detecting key components of a go game using a custom trained `Yolov8` model.
- **Game management:** Capable of streaming and visually reproducing a Go game with or without respecting the Go game rules.
- **SGF:** Capable of saving an SGF file of the streamed game for later use. 
- .
- **Intuitive Visualization:** An interactive user interface has been developed on the base of this project. The interface takes the form of a website, housed in a separate repository. Feel free to explore it by clicking here.



---

## 📂 Repository Structure

```sh
└── GoGame-Detection/
    ├── GoBoard.py
    ├── GoGame.py
    ├── GoVisual.py
    ├── Notebboks to explain detection/
    │   ├── Algorithmic approach to detect a go board.ipynb
    │   └── Go_board_detection.ipynb
    ├── UML/
    ├── main.py
    ├── model.pt
    ├── requirements.txt
    └── utils_.py

```

---


## ⚙️ Modules

<summary>Root</summary>

| File                                                                                                          | Summary                   |
| ---                                                                                                           | ---                       |
| [requirements.txt](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/requirements.txt) | Dependencies for the project |
| [main.py](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/main.py)                   | Main script to run GoGame-Detection |
| [GoGame.py](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/GoGame.py)               | Class for managing the Go game |
| [GoVisual.py](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/GoVisual.py)           | Class for visual representation of the Go game |
| [GoBoard.py](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/GoBoard.py)             | Class for detecting the board in its current position |
| [utils_.py](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/utils_.py)               | Utility functions used in GoBoard class |
| [model.pt](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/model.pt))                | Trained machine learning model file. |



<summary>Notebboks to explain detection</summary>

| File                               | Summary                   |
| ---                                | ---                       |
| [Go_board_detection.ipynb](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/Notebooks_to_explain_detection/Go_board_detection.ipynb)                                                    | Notebook explaining the Go board detection algorithm used in the project |
| [Algorithmic approach to detect a go board.ipynb](https://github.com/GoGame-Recognition-Project/GoGame-Detection/blob/main/Notebooks_to_explain_detection/Algorithmic_approach_to_detect_a_go_board.ipynb) | Notebook detailing the algorithmic approach for Go board detection |


---

## 🚀 Getting Started

***Dependencies***

Please ensure you have the following dependencies installed on your system:

ℹ️ [opencv-python](https://pypi.org/project/opencv-python/) (version 4.8.1.78)

ℹ️ [scikit-learn](https://scikit-learn.org/stable/install.html) (version 1.3.2)

ℹ️ [sente](https://pypi.org/project/sente/) (version 0.4.2)

ℹ️ [ultralytics](https://pypi.org/project/ultralytics/) (version 8.0.231)

### 🔧 Installation

1. Clone the GoGame-Detection repository:
```sh
git clone https://github.com/GoGame-Recognition-Project/GoGame-Detection.git
```

2. Change to the project directory:
```sh
cd GoGame-Detection
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```


### 🤖 Running the script

```sh
python run.py
```

---


## 👏 Acknowledgments

- Special thanks to [Etienne Peillard](https://github.com/EPeillard) our tutor for this project and Nicolas Desdames the representative of Tenuki Club, our project client.

[**Return**](#Top)

---
