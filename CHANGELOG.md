# Changelog

All notable changes to Actually Remote will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2026-03-03

### Added
- Initial repo structure and configuration templates
- Curated list of remote-friendly EU/global tech companies
- Core scraper with batch rotation scheduling
- AI-powered CV matching with pluggable provider support
- Daily email digest notifications
- Optional Discord and Telegram notifications
- `--dry-run` mode for URL validation
- `--test` mode for end-to-end pipeline testing
- GitHub Actions workflow for daily automated runs
- PR validation workflow for community company submissions

## [1.1.0] - 2026-03-04

### Added

- Company discovery agent (discover.py)
- AI-powered Google Search grounding to find new companies
- URL accessibility validation for discovered companies
- Discovery results sent via configured notification channels
- Results saved to discovery_results.txt
