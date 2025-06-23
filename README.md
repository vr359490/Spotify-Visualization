# Spotify Visualization

This project was created for creating a personalized song recommendations (after finding Spotify recommendations not so tasteful). It uses listening data from Spotify API, generates personalized recommendations, and visualizes musical the data as a network graph.

## Overview

- **Python and R Code:**  
  Handles the core functionality of the project.  
  - Pulls your listening data from Spotify (top songs, artists, genres)
  - Generates song recommendations based on your unique profile
  - Produces data for advanced network graph visualizations

- **HTML Example:**  
  Provides a sample visualization that users can run locally.  
  - The HTML file is not responsible for generating the visualization data; it simply displays an example output.

## How It Works

1. **Data Collection:**  
   Python scripts connect to the Spotify API to pull your top tracks, artists, genres, and other listening data.

2. **Recommendation Generation:**  
   Python analyzes your musical attributes and produces personalized song suggestions.

3. **Visualization Preparation:**  
   The R code takes the output data and constructs a network graph, mapping relationships between your songs, artists, and genres.

4. **Display Example:**  
   The included HTML file can be opened in your browser to view a sample visualization (not the logic behind generation).

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vr359490/Spotify-Visualization.git
   cd Spotify-Visualization
   ```

2. **Install dependencies (Python):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Spotify API credentials:**  

4. **Run the analysis and visualization scripts:**  
   - Use the Python code to extract and process your data.
   - Use the R scripts to generate the network graph.

5. **View example visualization:**  
   Open the HTML file in your browser for an example of a possible result.

## Project Structure

- `main.py` — Main orchestration script for data extraction and recommendation
- `.R` files — Scripts for network graph visualization
- `.html` file(s) — Example output visualization

> Project by [vr359490](https://github.com/vr359490)
