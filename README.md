<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg" />
  <img alt="Omkar Rane" src="assets/banner-light.svg" width="100%" />
</picture>

I build AI agents, smart-contract systems and developer tools. Most of what's below is deployed, so you can try it. You can reach me at [omkarrane0934@gmail.com](mailto:omkarrane0934@gmail.com), on [LinkedIn](https://linkedin.com/in/omkardrane) or on [X](https://x.com/OmkarRa72850136).

## Selected work

### [Chokepoint](https://github.com/Hackmaass/Chokepoint)

An investigation agent on FalkorDB. Given a fraud alert, it works out the few accounts to freeze so no route for stolen money is left, then checks the plan on a copy of the graph before a person approves it. A minimum cut needs a median of 1 account where a most-recent-recipients rule needs 3, and a verified plan takes a median of 0.27 s. It also caught FalkorDB returning a wrong max-flow answer (300 against the true 453) and gained a verified repair path. [Live demo](https://chokepoint-uou2.onrender.com/).

### [Sublevel](https://github.com/Hackmaass/Sublevel)

A two-player card duel on Monad testnet. Both fighters seal a move in secret and a contract resolves the turn, so no one can see or change a move afterwards. Fighters are NFTs whose records only the arena contract can write. Five contracts are deployed and source-verified. [Live demo](https://sublevel-theta.vercel.app).

### [Sealstone](https://github.com/Hackmaass/SealStone)

Milestone escrow for agreements that can't be gamed. Terms are signed by both sides as a hash, and the vault is tested against attacker contracts for reentrancy, forced ETH and rejecting recipients. Deployed on MST testnet. [Live demo](https://sealstone-rose.vercel.app/).

### [TamperSafe](https://github.com/Hackmaass/TamperSafe)

A tamper-evident container that locks at origin, watches itself in transit and settles payment on-chain by rules fixed before dispatch. A clean delivery pays the seller. A tamper refunds the buyer and slashes the courier's bond. ESP32-S3 sensors feed an escrow contract on MST testnet. [Live demo](https://tampersafe.vercel.app/).

### [Diskman](https://github.com/Hackmaass/Diskman)

A lightweight Windows storage visualizer and cache cleaner in native PowerShell and WPF. It has 36 cleanup targets, no external dependencies and a fail-closed safety engine.

### [Ada](https://github.com/Hackmaass/Ada)

Evidence-driven hiring. ADA, a multi-agent assistant, builds a model of each candidate from their actual work (GitHub, projects, interviews) and gives recommendations where every score is explainable. [Live demo](https://ada-gules.vercel.app).

I've also built [Signify_](https://github.com/Hackmaass/Signify_), a sign language tutor, [CT-Flow](https://github.com/Hackmaass/CT-Flow), a cybersecurity copilot, [Veyra](https://github.com/Hackmaass/Veyra), an intelligent companion, and [Kevin](https://github.com/Hackmaass/Kevin), a desktop companion in C++.

## What I work with

**Agents and data:** Python, RAG, multi-agent systems, FalkorDB, FastAPI, OpenCV, TensorFlow

**Smart contracts:** Solidity, ERC-721, Monad, MST Blockchain

**Web:** TypeScript, Next.js, React, Tailwind, Node.js

**Systems:** C, C++, PowerShell, Bash, Linux, Docker, ESP32
