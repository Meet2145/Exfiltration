# Exfiltration

<p align="center">
  <img src="https://img.icons8.com/clouds/500/anonymous-mask.png" height="120" alt="Hacker Icon"/>
  <h1 align="center">File Exfiltration Simulator</h1>
  <p align="center"><em>For cybersecurity education and ethical red team simulation only</em></p>
</p>

---

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Status](https://img.shields.io/badge/Status-Educational-green?style=flat-square)
![License](https://img.shields.io/badge/Use-Ethical%20Use%20Only-critical?style=flat-square&logo=gnu)

---

## ⚠️ Disclaimer

> ⚠️ **This tool is for educational and ethical use only.**
>
> This repository contains code that demonstrates **file exfiltration techniques**. It is intended solely for use in **cybersecurity labs**, **ethical hacking courses**, or **red team simulation environments** where you have **explicit permission**.
>
> 🚫 **Never use this tool on a production network or system without proper authorization.** Doing so may violate laws and ethical guidelines.

---

## 📌 Overview

This Python-based simulation mimics how attackers exfiltrate files from compromised systems. It reads files from a monitored directory, encodes them into Base64 chunks, and sends them to a remote form (e.g., Google Forms), while mimicking normal user activity and adding stealth techniques such as persistence and randomized timing.

---

## ✨ Features

- 📁 **Directory Monitoring** – Targets `.txt`, `.docx`, and `.sh` files in a configurable folder
- 🔐 **Base64 Chunk Encoding** – Splits files into randomized-size Base64-encoded chunks
- 🌐 **Simulated Upload** – Sends chunks to a configured Google Form endpoint with random headers
- 👤 **Human-Like Behavior** – Adds delays, mimics file previews and web access
- 💾 **Persistence** – Adds startup tasks for Windows/macOS
- 🧠 **Duplicate Avoidance** – Tracks processed files in memory via SHA-256 hashing

---

## ⚙️ Prerequisites

- **Python 3.x**
- **Requests Library** (install via pip):
  ```bash
  pip install requests
