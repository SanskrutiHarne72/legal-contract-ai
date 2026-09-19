# AI Legal Contract Assistant

> 🎓 Final Year Engineering Capstone Project  
> An enterprise-grade, AI-assisted platform for drafting, reviewing, and analyzing legal contracts using offline ML models.

## Overview

The **AI Legal Contract Assistant** is an intelligent legal tech engine powered by **trained local ML models** (TF-IDF + Linear SVM classifier, CRF entity tagger, Random Forest risk classifier, rule engine, and local BM25 QA retriever). It enables users to:

- **Draft Contracts** — Build customized legal agreements through a guided wizard with local template engine generation
- **Review Contracts** — Upload PDF agreements and receive comprehensive structural risk audits
- **Explain Clauses** — Transform dense legal jargon into plain-language business terms
- **Risk Analysis** — Automatically detect high-risk liabilities, unfair indemnities, and missing protections
- **Export PDFs** — Generate publication-ready legal documents via ReportLab

## Features

| Module | Description |
|--------|-------------|
| Contract Drafting | Multi-step wizard with standard legal clauses, party details, and commercial terms |
| PDF Review | PyMuPDF ingestion with local ML-powered clause analysis and risk scoring |
| Clause Explainer | Plain-language breakdown with risk flags and strategic advantages |
| Risk Matrix | Automated threat detection with severity classification and redline recommendations |
| Repository | Local SQLite storage with search, export, and delete capabilities |
| AI Legal Chat | Conversational assistant with local FAQ knowledge retrieval |

## Technology Stack

- **Frontend:** Streamlit (Python)
- **AI Engine:** Local LegalML Engine (TF-IDF + Linear SVM, CRF, Random Forest, BM25)
- **PDF Parsing:** PyMuPDF (fitz)
- **PDF Generation:** ReportLab
- **Database:** SQLite
- **Environment:** python-dotenv

## System Architecture

The entire application runs **100% offline**, ensuring total data privacy with zero external API calls or third-party cloud data transmission.
