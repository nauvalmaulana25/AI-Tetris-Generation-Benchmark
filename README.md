# AI-Tetris-Generation-Benchmark
This repository contains the source code, and evaluation scripts for the research paper "Efficiency and Performance Analysis of AI Models for Code Generation: ChatGPT, Gemini, and Claude."

This study provides a quantitative comparison of three advanced Large Language Models—ChatGPT (GPT-5 Pro), Gemini (2.5 Pro), and Claude (4.5 Sonnet)—evaluating their ability to generate a fully functional Python-based Tetris application from a single prompt.

Contents of this repository:

- AI-Generated Source Code: The raw, unmodified Python output produced by each model, allowing for direct analysis of coding styles, verbosity, and structural differences.

- Metric Calculation Scripts: The specific algorithms and scripts used to compute the Chapter 3 evaluation metrics, including Lines of Code (LOC) and Line Processing Efficiency (LPE).

- Unit Test Suite: The unittest framework and test cases used to measure Functional Correctness across 10 key game scenarios (e.g., collision detection, wall kicks, and line clearing).

This project highlights the trade-offs between code complexity and reliability, offering evidence-based insights for developers selecting AI coding assistants.
