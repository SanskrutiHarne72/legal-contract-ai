# AI Legal Contract Assistant

&gt; 🎓 Final Year Engineering Capstone Project  
&gt; An enterprise-grade, AI-assisted platform for drafting, reviewing, and analyzing legal contracts.

## Overview

The **AI Legal Contract Assistant** is an intelligent legal tech engine powered by **Google Gemini AI**. It enables users to:

- **Draft Contracts** — Build customized legal agreements through a guided wizard with AI-generated clauses
- **Review Contracts** — Upload PDF agreements and receive comprehensive structural risk audits
- **Explain Clauses** — Transform dense legal jargon into plain-language business terms
- **Risk Analysis** — Automatically detect high-risk liabilities, unfair indemnities, and missing protections
- **Export PDFs** — Generate publication-ready legal documents via ReportLab

## Features

| Module | Description |
|--------|-------------|
| Contract Drafting | Multi-step wizard with 12+ standard legal clauses, party details, and commercial terms |
| PDF Review | PyMuPDF ingestion with Gemini-powered clause analysis and risk scoring |
| Clause Explainer | Plain-language breakdown with risk flags and strategic advantages |
| Risk Matrix | Automated threat detection with severity classification and redline recommendations |
| Repository | Local SQLite storage with search, export, and delete capabilities |
| AI Legal Chat | Conversational assistant for contract law inquiries |

## Technology Stack

- **Frontend:** Streamlit (Python)
- **AI Engine:** Google Gemini 1.5 Flash
- **PDF Parsing:** PyMuPDF (fitz)
- **PDF Generation:** ReportLab
- **Database:** SQLite
- **Environment:** python-dotenv

## Project Structure
