MoEngage Documentation Analyzer Agent
This project implements an AI-powered agent designed to analyze MoEngage's public documentation articles and suggest improvements based on specific criteria. This addresses Task 1 of the coding assignment.

Table of Contents
Project Overview

Setup and Installation

How to Run

Assumptions Made

Design Choices and Approach

Challenges Faced

Example Output

Project Overview
The core of this project is the DocumentationAnalyzerAgent class, which takes a URL of a MoEngage documentation article, fetches its content, and then uses a Large Language Model (LLM) to analyze it against four key criteria:

Readability for a Marketer: Assesses how easily a non-technical marketer can understand the content.

Structure and Flow: Evaluates the organization, headings, paragraphing, and logical progression of information.

Completeness of Information & Examples: Checks if the article provides sufficient detail and relevant examples for understanding and implementation.

Adherence to Simplified Style Guidelines: Analyzes the voice, tone, clarity, conciseness, and use of action-oriented language.

The agent outputs a structured JSON report containing an assessment and actionable suggestions for each criterion.

Setup and Installation
To set up and run this project, follow these steps:

Clone the Repository:

git clone "https://github.com/rbcse/moengage_article_analysis.git"
cd agent1

Create a Virtual Environment (Recommended):

python -m venv venv
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

Install Dependencies:

pip install -r requirements.txt

Set Up Your API Key:

OPENROUTER_API_KEY="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"
YOUR_SITE_URL="https://developers.moengage.com/hc/en-us/articles/9467044080660-Tracking-Events-7-x-x#h_01H96953S1KHBK0JANKVYDHSM1"
YOUR_SITE_NAME="MoEngage Doc Analyzer"

I am giving this file so that you can directly run it.

How to Run
After completing the setup and installation steps:

Activate your virtual environment (if you haven't already).

Run the main script:

python main.py

The script will fetch content from the predefined MoEngage documentation URLs, analyze them using the LLM, and save the comprehensive JSON report to a file named sample_output.json in the project's root directory.

Assumptions Made
URL Structure: It is assumed that the provided URLs (e.g., https://developers.moengage.com/hc/en-us/articles/...) will consistently return valid HTML content that crawl4ai can effectively parse into Markdown.

LLM Capabilities: It is assumed that the chosen LLM (deepseek/deepseek-r1:free via OpenRouter) is capable of:

Understanding complex instructions regarding content analysis and persona (non-technical marketer).

Generating structured JSON output reliably when explicitly prompted.

Performing qualitative assessments and generating actionable suggestions based on the provided criteria.

Markdown Content Quality: The analysis relies on the quality of the Markdown extracted by crawl4ai. While crawl4ai is robust, extremely malformed or sparse web pages might yield less useful Markdown, impacting LLM analysis.

API Rate Limits: It's assumed that the number of API calls made during a typical run will stay within OpenRouter's free tier or your paid plan's rate limits. For larger-scale analysis, rate limiting or batching would be necessary.

Design Choices and Approach
Overall Architecture
The project follows a modular and asynchronous design:

AsyncWebCrawler (from crawl4ai): Chosen for efficient and robust web content extraction. Its ability to return content in Markdown format is crucial as it provides a cleaner, more digestible input for the LLM compared to raw HTML.

DocumentationAnalyzerAgent Class: Encapsulates the core logic for analysis, making the code organized and reusable. It handles both web scraping and LLM interaction.

Asynchronous Operations (asyncio.to_thread): Leveraging asyncio allows for concurrent handling of web scraping and LLM calls, improving efficiency. asyncio.to_thread is used to run the synchronous requests library calls in a separate thread, preventing blocking of the main event loop.

Environment Variables (python-dotenv): Best practice for managing sensitive API keys, keeping them out of the codebase.

Interpretation and Application of Style Guidelines
For the "Adherence to Simplified Style Guidelines" criterion, I focused on the three key aspects mentioned in the assignment:

Voice and Tone: The LLM is prompted to assess if the content maintains a customer-focused, clear, and concise tone, suitable for a marketing audience.

Clarity and Conciseness: The prompt explicitly asks the LLM to identify overly complex sentences or jargon that could be simplified, encouraging direct and easy-to-understand language.

Action-oriented Language: The LLM is guided to check if the documentation effectively instructs the user, identifying passive voice or vague phrasing that could be made more directive.

The approach is to provide these guidelines directly in the prompt, along with examples of desired changes, allowing the LLM to perform a qualitative assessment and generate specific, actionable refactoring suggestions.

Approach to the Revision Task (Task 2 - Bonus)
The bonus Task 2 (Documentation Revision Agent) was not attempted in this submission due to the primary focus on thoroughly completing Task 1 within the estimated timeframe.

If I were to approach Task 2, my conceptual design would involve:

Parsing Suggestions: The revision agent would first parse the structured JSON output from Agent 1.

Categorization: Suggestions would be categorized (e.g., "replace jargon," "add example," "restructure heading").

Targeted LLM Calls: For each suggestion type, a specific LLM prompt would be crafted. For instance:

Jargon Replacement: "Given this sentence: 'X', and the suggestion 'replace Y with Z', rewrite the sentence incorporating this change."

Adding Examples: "Given this paragraph: 'A', and the suggestion 'add a code example for feature B', generate a suitable example and integrate it."

Restructuring: This would be the most complex, potentially requiring the LLM to rewrite entire sections based on structural advice.

Iterative Refinement: The process might involve multiple LLM calls per document, iteratively applying changes.

Human-in-the-Loop: For a production-ready system, a human review step would be essential to validate the revised content.

This task is complex due to the need for precise content manipulation and maintaining context, which LLMs can struggle with without careful prompt engineering and potentially fine-tuning.

Challenges Faced
Ensuring Consistent JSON Output from LLM:

Challenge: Initially, the LLM would occasionally include conversational text, markdown fences (e.g., ````json), or incomplete JSON objects in its response, leading to JSONDecodeError`.

Resolution: This was primarily addressed through rigorous prompt engineering. Adding "CRITICAL INSTRUCTION: Return ONLY the JSON object, and nothing else. Do not include any conversational text, markdown formatting (like ```json), or explanations outside of the JSON." along with clear example JSON structures in every prompt significantly improved consistency. A fallback strip() and startswith/endswith check for markdown fences was also added as a safeguard.

Handling Synchronous requests in Asynchronous Context:

Challenge: The requests library, used for making HTTP calls to OpenRouter, is synchronous. Directly calling it within an async function would block the entire asyncio event loop.

Resolution: The asyncio.to_thread() function was used to offload the synchronous requests.post call to a separate thread. This allows the main event loop to remain responsive while the HTTP request is being processed, maintaining the benefits of asynchronous programming.

LLM Context Window Limitations (Potential):

Challenge (Anticipated): While not explicitly encountered with the provided example URLs, very long documentation articles could potentially exceed the LLM's context window, leading to truncated analysis or errors.

Resolution (Future Consideration): If this challenge were to arise, strategies would include:

Content Chunking: Breaking down the article into smaller, manageable chunks and analyzing each chunk separately, then aggregating the suggestions.

Summarization: Using an initial LLM call to summarize very long articles before performing detailed analysis on the summary.

Retrieval-Augmented Generation (RAG): For very large documentation bases, implementing a RAG system to retrieve relevant sections before feeding them to the LLM for analysis.

Example Output
An example of the structured JSON output generated by Agent 1 for the provided URLs can be found in the sample_output.json file in this repository. This file contains a list of analysis reports, one for each URL processed.
